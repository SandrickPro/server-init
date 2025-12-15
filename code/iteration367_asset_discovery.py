#!/usr/bin/env python3
"""
Server Init - Iteration 367: Asset Discovery Platform
Платформа обнаружения и инвентаризации активов

Функционал:
- Network Scanning - сканирование сети
- Agent-Based Discovery - обнаружение через агенты
- Cloud Integration - интеграция с облаком
- Software Inventory - инвентаризация ПО
- Hardware Inventory - инвентаризация оборудования
- Credential Management - управление учетными данными
- Discovery Scheduling - планирование обнаружения
- Asset Reconciliation - сверка активов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import ipaddress


class DiscoveryMethod(Enum):
    """Метод обнаружения"""
    NETWORK_SCAN = "network_scan"
    AGENT = "agent"
    CLOUD_API = "cloud_api"
    SNMP = "snmp"
    WMI = "wmi"
    SSH = "ssh"
    API = "api"
    MANUAL = "manual"


class AssetType(Enum):
    """Тип актива"""
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    APPLICATION = "application"
    LOAD_BALANCER = "load_balancer"
    CLOUD_INSTANCE = "cloud_instance"


class AssetStatus(Enum):
    """Статус актива"""
    DISCOVERED = "discovered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNREACHABLE = "unreachable"
    RETIRED = "retired"
    UNKNOWN = "unknown"


class ScanStatus(Enum):
    """Статус сканирования"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"
    DIGITALOCEAN = "digitalocean"
    OPENSTACK = "openstack"


class CredentialType(Enum):
    """Тип учетных данных"""
    SSH_KEY = "ssh_key"
    SSH_PASSWORD = "ssh_password"
    SNMP_COMMUNITY = "snmp_community"
    WMI = "wmi"
    API_KEY = "api_key"
    CLOUD_CREDENTIALS = "cloud_credentials"


@dataclass
class Credential:
    """Учетные данные"""
    credential_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    
    # Type
    credential_type: CredentialType = CredentialType.SSH_PASSWORD
    
    # Scope
    scope: List[str] = field(default_factory=list)  # IP ranges, domains
    
    # Status
    is_valid: bool = True
    last_used: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkInterface:
    """Сетевой интерфейс"""
    interface_id: str
    
    # Identity
    name: str = ""
    mac_address: str = ""
    
    # IP Configuration
    ip_addresses: List[str] = field(default_factory=list)
    subnet_mask: str = ""
    gateway: str = ""
    
    # State
    is_up: bool = True
    speed_mbps: int = 0


@dataclass
class Software:
    """Программное обеспечение"""
    software_id: str
    
    # Identity
    name: str = ""
    vendor: str = ""
    version: str = ""
    
    # Installation
    install_date: Optional[datetime] = None
    install_path: str = ""
    
    # License
    license_type: str = ""  # commercial, open_source, trial
    license_key: str = ""


@dataclass
class HardwareInfo:
    """Информация об оборудовании"""
    # CPU
    cpu_model: str = ""
    cpu_cores: int = 0
    cpu_frequency_mhz: int = 0
    
    # Memory
    memory_total_gb: float = 0.0
    memory_used_gb: float = 0.0
    
    # Storage
    storage_total_gb: float = 0.0
    storage_used_gb: float = 0.0
    
    # System
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    bios_version: str = ""


@dataclass
class Asset:
    """Актив"""
    asset_id: str
    
    # Identity
    hostname: str = ""
    display_name: str = ""
    fqdn: str = ""
    
    # Type and Status
    asset_type: AssetType = AssetType.SERVER
    status: AssetStatus = AssetStatus.DISCOVERED
    
    # Network
    primary_ip: str = ""
    interfaces: List[NetworkInterface] = field(default_factory=list)
    
    # Hardware
    hardware: Optional[HardwareInfo] = None
    
    # OS
    os_name: str = ""
    os_version: str = ""
    os_architecture: str = ""  # x86, x64, arm
    
    # Software
    installed_software: List[Software] = field(default_factory=list)
    
    # Services
    running_services: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    
    # Location
    location: str = ""
    datacenter: str = ""
    rack: str = ""
    
    # Cloud
    cloud_provider: Optional[CloudProvider] = None
    cloud_region: str = ""
    cloud_instance_id: str = ""
    
    # Owner
    owner_team: str = ""
    owner_contact: str = ""
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Discovery
    discovery_method: DiscoveryMethod = DiscoveryMethod.NETWORK_SCAN
    first_discovered: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ScanRange:
    """Диапазон сканирования"""
    range_id: str
    
    # Definition
    name: str = ""
    ip_ranges: List[str] = field(default_factory=list)  # CIDR notation
    excluded_ips: List[str] = field(default_factory=list)
    
    # Ports
    ports: List[int] = field(default_factory=list)
    
    # Credentials
    credential_ids: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True


@dataclass
class DiscoveryScan:
    """Сканирование обнаружения"""
    scan_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    
    # Type
    discovery_method: DiscoveryMethod = DiscoveryMethod.NETWORK_SCAN
    
    # Scope
    scan_ranges: List[str] = field(default_factory=list)  # range IDs
    
    # Status
    status: ScanStatus = ScanStatus.PENDING
    
    # Progress
    progress_percent: float = 0.0
    targets_total: int = 0
    targets_scanned: int = 0
    assets_found: int = 0
    new_assets: int = 0
    updated_assets: int = 0
    
    # Errors
    errors: List[str] = field(default_factory=list)
    
    # Timestamps
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoverySchedule:
    """Расписание обнаружения"""
    schedule_id: str
    
    # Identity
    name: str = ""
    
    # Scope
    scan_ranges: List[str] = field(default_factory=list)
    discovery_method: DiscoveryMethod = DiscoveryMethod.NETWORK_SCAN
    
    # Schedule
    cron_expression: str = ""  # e.g., "0 2 * * *" for 2 AM daily
    interval_minutes: int = 0  # Alternative to cron
    
    # Status
    is_enabled: bool = True
    
    # Last Run
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class CloudConnection:
    """Подключение к облаку"""
    connection_id: str
    
    # Identity
    name: str = ""
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Regions
    regions: List[str] = field(default_factory=list)
    
    # Credential
    credential_id: str = ""
    
    # Status
    is_connected: bool = False
    last_sync: Optional[datetime] = None
    
    # Discovery
    auto_discovery: bool = True


@dataclass
class ReconciliationResult:
    """Результат сверки"""
    result_id: str
    
    # Assets
    matched_assets: int = 0
    new_assets: int = 0
    missing_assets: int = 0
    changed_assets: int = 0
    
    # Details
    changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    reconciled_at: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoveryMetrics:
    """Метрики обнаружения"""
    metrics_id: str
    
    # Assets
    total_assets: int = 0
    active_assets: int = 0
    new_assets_24h: int = 0
    
    # Scans
    scans_completed_24h: int = 0
    average_scan_duration_sec: float = 0.0
    
    # Coverage
    networks_scanned: int = 0
    ips_scanned: int = 0
    
    # Cloud
    cloud_instances: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class AssetDiscoveryPlatform:
    """Платформа обнаружения активов"""
    
    def __init__(self, platform_name: str = "discovery"):
        self.platform_name = platform_name
        self.assets: Dict[str, Asset] = {}
        self.scan_ranges: Dict[str, ScanRange] = {}
        self.scans: Dict[str, DiscoveryScan] = {}
        self.schedules: Dict[str, DiscoverySchedule] = {}
        self.credentials: Dict[str, Credential] = {}
        self.cloud_connections: Dict[str, CloudConnection] = {}
        self.reconciliation_history: List[ReconciliationResult] = []
        
    async def create_scan_range(self, name: str,
                               ip_ranges: List[str],
                               ports: List[int] = None,
                               excluded_ips: List[str] = None) -> ScanRange:
        """Создание диапазона сканирования"""
        scan_range = ScanRange(
            range_id=f"rng_{uuid.uuid4().hex[:8]}",
            name=name,
            ip_ranges=ip_ranges,
            ports=ports or [22, 80, 443, 3389, 5985],
            excluded_ips=excluded_ips or []
        )
        
        self.scan_ranges[scan_range.range_id] = scan_range
        return scan_range
        
    async def create_credential(self, name: str,
                               credential_type: CredentialType,
                               scope: List[str] = None) -> Credential:
        """Создание учетных данных"""
        credential = Credential(
            credential_id=f"crd_{uuid.uuid4().hex[:8]}",
            name=name,
            credential_type=credential_type,
            scope=scope or []
        )
        
        self.credentials[credential.credential_id] = credential
        return credential
        
    async def start_scan(self, name: str,
                        discovery_method: DiscoveryMethod,
                        scan_range_ids: List[str] = None) -> DiscoveryScan:
        """Запуск сканирования"""
        scan = DiscoveryScan(
            scan_id=f"scn_{uuid.uuid4().hex[:8]}",
            name=name,
            discovery_method=discovery_method,
            scan_ranges=scan_range_ids or [],
            status=ScanStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.scans[scan.scan_id] = scan
        
        # Simulate scanning
        await self._execute_scan(scan)
        
        return scan
        
    async def _execute_scan(self, scan: DiscoveryScan):
        """Выполнение сканирования"""
        # Calculate targets
        total_targets = 0
        for range_id in scan.scan_ranges:
            scan_range = self.scan_ranges.get(range_id)
            if scan_range:
                for ip_range in scan_range.ip_ranges:
                    try:
                        network = ipaddress.ip_network(ip_range, strict=False)
                        total_targets += network.num_addresses
                    except ValueError:
                        pass
                        
        if total_targets == 0:
            total_targets = random.randint(50, 200)
            
        scan.targets_total = total_targets
        
        # Simulate discovery
        await asyncio.sleep(0.1)
        
        assets_found = random.randint(10, min(50, total_targets))
        new_assets = random.randint(0, assets_found // 3)
        
        # Create discovered assets
        for _ in range(new_assets):
            asset = await self._create_discovered_asset(scan.discovery_method)
            scan.new_assets += 1
            scan.assets_found += 1
            
        scan.updated_assets = assets_found - new_assets
        scan.assets_found = assets_found
        scan.targets_scanned = total_targets
        scan.progress_percent = 100.0
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.now()
        
    async def _create_discovered_asset(self, method: DiscoveryMethod) -> Asset:
        """Создание обнаруженного актива"""
        asset_types = list(AssetType)
        asset_type = random.choice(asset_types[:6])  # Common types
        
        # Generate hostname
        prefixes = {"server": "srv", "workstation": "ws", "virtual_machine": "vm", "container": "ctr", "network_device": "net", "storage": "stor"}
        prefix = prefixes.get(asset_type.value, "host")
        hostname = f"{prefix}-{uuid.uuid4().hex[:6]}"
        
        # Generate IP
        ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        # OS options
        os_options = [
            ("Ubuntu", "22.04 LTS", "x64"),
            ("CentOS", "8", "x64"),
            ("Windows Server", "2022", "x64"),
            ("Red Hat Enterprise Linux", "9", "x64"),
            ("Debian", "12", "x64")
        ]
        os_name, os_version, os_arch = random.choice(os_options)
        
        hardware = HardwareInfo(
            cpu_model=random.choice(["Intel Xeon E5-2680", "AMD EPYC 7543", "Intel Core i9-12900K"]),
            cpu_cores=random.choice([4, 8, 16, 32]),
            cpu_frequency_mhz=random.choice([2400, 2800, 3200, 3600]),
            memory_total_gb=random.choice([8, 16, 32, 64, 128]),
            storage_total_gb=random.choice([256, 512, 1024, 2048])
        )
        hardware.memory_used_gb = hardware.memory_total_gb * random.uniform(0.3, 0.8)
        hardware.storage_used_gb = hardware.storage_total_gb * random.uniform(0.2, 0.7)
        
        # Network interface
        interface = NetworkInterface(
            interface_id=f"if_{uuid.uuid4().hex[:8]}",
            name="eth0",
            mac_address=":".join([f"{random.randint(0, 255):02x}" for _ in range(6)]),
            ip_addresses=[ip],
            subnet_mask="255.255.255.0"
        )
        
        asset = Asset(
            asset_id=f"ast_{uuid.uuid4().hex[:8]}",
            hostname=hostname,
            display_name=hostname,
            fqdn=f"{hostname}.local",
            asset_type=asset_type,
            status=AssetStatus.ACTIVE,
            primary_ip=ip,
            interfaces=[interface],
            hardware=hardware,
            os_name=os_name,
            os_version=os_version,
            os_architecture=os_arch,
            open_ports=random.sample([22, 80, 443, 3306, 5432, 8080, 8443], random.randint(1, 4)),
            discovery_method=method,
            tags=["auto-discovered"]
        )
        
        self.assets[asset.asset_id] = asset
        return asset
        
    async def connect_cloud(self, name: str,
                           provider: CloudProvider,
                           regions: List[str] = None,
                           credential_id: str = "") -> CloudConnection:
        """Подключение к облаку"""
        connection = CloudConnection(
            connection_id=f"cld_{uuid.uuid4().hex[:8]}",
            name=name,
            provider=provider,
            regions=regions or [],
            credential_id=credential_id,
            is_connected=True,
            auto_discovery=True
        )
        
        self.cloud_connections[connection.connection_id] = connection
        
        # Simulate cloud discovery
        await self._discover_cloud_instances(connection)
        
        return connection
        
    async def _discover_cloud_instances(self, connection: CloudConnection):
        """Обнаружение облачных инстансов"""
        instances_count = random.randint(5, 15)
        
        instance_types = {
            CloudProvider.AWS: ["t3.micro", "t3.medium", "m5.large", "r5.xlarge"],
            CloudProvider.AZURE: ["Standard_B1s", "Standard_D2s_v3", "Standard_E4s_v3"],
            CloudProvider.GCP: ["e2-micro", "e2-medium", "n2-standard-4"]
        }
        
        types = instance_types.get(connection.provider, ["standard"])
        
        for i in range(instances_count):
            region = random.choice(connection.regions) if connection.regions else "us-east-1"
            instance_type = random.choice(types)
            
            asset = Asset(
                asset_id=f"ast_{uuid.uuid4().hex[:8]}",
                hostname=f"{connection.provider.value}-{region}-{i:03d}",
                display_name=f"Cloud Instance {i}",
                asset_type=AssetType.CLOUD_INSTANCE,
                status=AssetStatus.ACTIVE,
                primary_ip=f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                os_name="Amazon Linux" if connection.provider == CloudProvider.AWS else "Ubuntu",
                os_version="2023" if connection.provider == CloudProvider.AWS else "22.04",
                cloud_provider=connection.provider,
                cloud_region=region,
                cloud_instance_id=f"i-{uuid.uuid4().hex[:12]}",
                discovery_method=DiscoveryMethod.CLOUD_API,
                tags=["cloud", connection.provider.value, region, instance_type]
            )
            
            # Add hardware based on instance type
            cores = {"micro": 1, "small": 1, "medium": 2, "large": 4, "xlarge": 8}
            for size, c in cores.items():
                if size in instance_type.lower():
                    asset.hardware = HardwareInfo(cpu_cores=c, memory_total_gb=c * 2)
                    break
                    
            self.assets[asset.asset_id] = asset
            
        connection.last_sync = datetime.now()
        
    async def create_schedule(self, name: str,
                             discovery_method: DiscoveryMethod,
                             scan_range_ids: List[str] = None,
                             interval_minutes: int = 0,
                             cron_expression: str = "") -> DiscoverySchedule:
        """Создание расписания"""
        schedule = DiscoverySchedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            name=name,
            discovery_method=discovery_method,
            scan_ranges=scan_range_ids or [],
            interval_minutes=interval_minutes,
            cron_expression=cron_expression,
            is_enabled=True
        )
        
        # Calculate next run
        if interval_minutes > 0:
            schedule.next_run = datetime.now() + timedelta(minutes=interval_minutes)
        elif cron_expression:
            schedule.next_run = datetime.now() + timedelta(hours=1)  # Simplified
            
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    async def reconcile_assets(self, source: str = "cmdb") -> ReconciliationResult:
        """Сверка активов"""
        result = ReconciliationResult(
            result_id=f"rec_{uuid.uuid4().hex[:8]}"
        )
        
        # Simulate reconciliation
        total = len(self.assets)
        result.matched_assets = int(total * 0.8)
        result.new_assets = int(total * 0.1)
        result.changed_assets = int(total * 0.08)
        result.missing_assets = int(total * 0.02)
        
        # Generate some sample changes
        for asset in random.sample(list(self.assets.values()), min(5, len(self.assets))):
            result.changes.append({
                "asset_id": asset.asset_id,
                "hostname": asset.hostname,
                "change_type": random.choice(["ip_changed", "status_changed", "new_software"]),
                "old_value": "10.0.0.1",
                "new_value": asset.primary_ip
            })
            
        self.reconciliation_history.append(result)
        return result
        
    async def get_asset_software(self, asset_id: str) -> List[Software]:
        """Получение ПО актива"""
        asset = self.assets.get(asset_id)
        if not asset:
            return []
            
        # Generate sample software if empty
        if not asset.installed_software:
            software_catalog = [
                ("Python", "Python Software Foundation", "3.11.4"),
                ("Node.js", "OpenJS Foundation", "18.17.0"),
                ("Docker", "Docker Inc", "24.0.5"),
                ("PostgreSQL", "PostgreSQL Global Development Group", "15.3"),
                ("nginx", "Nginx Inc", "1.24.0"),
                ("Redis", "Redis Ltd", "7.0.12"),
                ("Java Runtime", "Oracle", "17.0.8"),
                ("Git", "Software Freedom Conservancy", "2.41.0")
            ]
            
            for name, vendor, version in random.sample(software_catalog, random.randint(3, 6)):
                sw = Software(
                    software_id=f"sw_{uuid.uuid4().hex[:8]}",
                    name=name,
                    vendor=vendor,
                    version=version,
                    install_date=datetime.now() - timedelta(days=random.randint(1, 365))
                )
                asset.installed_software.append(sw)
                
        return asset.installed_software
        
    async def collect_metrics(self) -> DiscoveryMetrics:
        """Сбор метрик"""
        active_count = sum(1 for a in self.assets.values() if a.status == AssetStatus.ACTIVE)
        
        now = datetime.now()
        new_24h = sum(
            1 for a in self.assets.values()
            if (now - a.first_discovered).total_seconds() < 86400
        )
        
        scans_24h = sum(
            1 for s in self.scans.values()
            if s.completed_at and (now - s.completed_at).total_seconds() < 86400
        )
        
        cloud_instances = sum(
            1 for a in self.assets.values()
            if a.asset_type == AssetType.CLOUD_INSTANCE
        )
        
        # Average scan duration
        durations = []
        for scan in self.scans.values():
            if scan.started_at and scan.completed_at:
                durations.append((scan.completed_at - scan.started_at).total_seconds())
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        return DiscoveryMetrics(
            metrics_id=f"mtr_{uuid.uuid4().hex[:8]}",
            total_assets=len(self.assets),
            active_assets=active_count,
            new_assets_24h=new_24h,
            scans_completed_24h=scans_24h,
            average_scan_duration_sec=avg_duration,
            networks_scanned=len(self.scan_ranges),
            cloud_instances=cloud_instances
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_type = {}
        for asset_type in AssetType:
            by_type[asset_type.value] = sum(1 for a in self.assets.values() if a.asset_type == asset_type)
            
        by_status = {}
        for status in AssetStatus:
            by_status[status.value] = sum(1 for a in self.assets.values() if a.status == status)
            
        by_method = {}
        for method in DiscoveryMethod:
            by_method[method.value] = sum(1 for a in self.assets.values() if a.discovery_method == method)
            
        by_cloud = {}
        for provider in CloudProvider:
            by_cloud[provider.value] = sum(1 for a in self.assets.values() if a.cloud_provider == provider)
            
        os_distribution = {}
        for asset in self.assets.values():
            os_key = asset.os_name or "Unknown"
            os_distribution[os_key] = os_distribution.get(os_key, 0) + 1
            
        return {
            "total_assets": len(self.assets),
            "by_type": by_type,
            "by_status": by_status,
            "by_discovery_method": by_method,
            "by_cloud_provider": by_cloud,
            "os_distribution": os_distribution,
            "scan_ranges": len(self.scan_ranges),
            "total_scans": len(self.scans),
            "schedules": len(self.schedules),
            "credentials": len(self.credentials),
            "cloud_connections": len(self.cloud_connections)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 367: Asset Discovery Platform")
    print("=" * 60)
    
    platform = AssetDiscoveryPlatform(platform_name="enterprise-discovery")
    print("✓ Asset Discovery Platform initialized")
    
    # Create Credentials
    print("\n🔑 Creating Discovery Credentials...")
    
    credentials_data = [
        ("SSH Linux Servers", CredentialType.SSH_KEY, ["10.0.0.0/8"]),
        ("SSH Unix Legacy", CredentialType.SSH_PASSWORD, ["192.168.0.0/16"]),
        ("Windows WMI", CredentialType.WMI, ["10.10.0.0/16"]),
        ("SNMP Network", CredentialType.SNMP_COMMUNITY, ["10.0.0.0/8"]),
        ("AWS Production", CredentialType.CLOUD_CREDENTIALS, [])
    ]
    
    for name, cred_type, scope in credentials_data:
        await platform.create_credential(name, cred_type, scope)
        print(f"  🔑 {name} ({cred_type.value})")
        
    # Create Scan Ranges
    print("\n📡 Creating Scan Ranges...")
    
    ranges_data = [
        ("Production Network", ["10.10.0.0/16"], [22, 80, 443, 3389, 8080]),
        ("Staging Network", ["10.20.0.0/16"], [22, 80, 443, 8080]),
        ("Development Network", ["10.30.0.0/16"], [22, 80, 443, 8080, 3000]),
        ("DMZ", ["192.168.100.0/24"], [80, 443, 8443])
    ]
    
    scan_ranges = []
    for name, ranges, ports in ranges_data:
        sr = await platform.create_scan_range(name, ranges, ports)
        scan_ranges.append(sr)
        print(f"  📡 {name}: {', '.join(ranges)}")
        
    # Run Network Scans
    print("\n🔍 Running Network Discovery Scans...")
    
    for sr in scan_ranges[:2]:  # Scan first 2 ranges
        scan = await platform.start_scan(
            f"Scan {sr.name}",
            DiscoveryMethod.NETWORK_SCAN,
            [sr.range_id]
        )
        print(f"  ✓ {scan.name}: Found {scan.assets_found} assets ({scan.new_assets} new)")
        
    # Connect Cloud Providers
    print("\n☁️ Connecting Cloud Providers...")
    
    cloud_configs = [
        ("AWS Production", CloudProvider.AWS, ["us-east-1", "us-west-2"]),
        ("Azure Europe", CloudProvider.AZURE, ["westeurope", "northeurope"]),
        ("GCP Asia", CloudProvider.GCP, ["asia-east1", "asia-southeast1"])
    ]
    
    for name, provider, regions in cloud_configs:
        conn = await platform.connect_cloud(name, provider, regions)
        cloud_assets = sum(1 for a in platform.assets.values() if a.cloud_provider == provider)
        print(f"  ☁️ {name}: {cloud_assets} instances discovered")
        
    # Create Discovery Schedules
    print("\n📅 Creating Discovery Schedules...")
    
    schedules_data = [
        ("Nightly Full Scan", DiscoveryMethod.NETWORK_SCAN, 0, "0 2 * * *"),
        ("Hourly Quick Scan", DiscoveryMethod.NETWORK_SCAN, 60, ""),
        ("Cloud Sync", DiscoveryMethod.CLOUD_API, 30, "")
    ]
    
    for name, method, interval, cron in schedules_data:
        schedule = await platform.create_schedule(name, method, [sr.range_id for sr in scan_ranges], interval, cron)
        schedule_type = f"every {interval} min" if interval else cron
        print(f"  📅 {name} ({schedule_type})")
        
    # Get Software Inventory
    print("\n💿 Software Discovery...")
    
    sample_assets = list(platform.assets.values())[:3]
    for asset in sample_assets:
        software = await platform.get_asset_software(asset.asset_id)
        print(f"\n  {asset.hostname}:")
        for sw in software[:4]:
            print(f"    📦 {sw.name} v{sw.version}")
            
    # Reconciliation
    print("\n🔄 Running Asset Reconciliation...")
    
    recon = await platform.reconcile_assets("cmdb")
    print(f"  ✓ Matched: {recon.matched_assets}")
    print(f"  ➕ New: {recon.new_assets}")
    print(f"  ✏️ Changed: {recon.changed_assets}")
    print(f"  ❌ Missing: {recon.missing_assets}")
    
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Asset Table
    print("\n📦 Discovered Assets:")
    
    print("\n  ┌──────────────────────────┬──────────────────┬──────────────────┬─────────────────────────────────┬───────────────┐")
    print("  │ Hostname                 │ Type             │ IP               │ OS                              │ Status        │")
    print("  ├──────────────────────────┼──────────────────┼──────────────────┼─────────────────────────────────┼───────────────┤")
    
    for asset in list(platform.assets.values())[:15]:
        hostname = asset.hostname[:24].ljust(24)
        atype = asset.asset_type.value[:16].ljust(16)
        ip = asset.primary_ip[:16].ljust(16)
        os_info = f"{asset.os_name} {asset.os_version}"[:31].ljust(31)
        status = asset.status.value[:13].ljust(13)
        
        print(f"  │ {hostname} │ {atype} │ {ip} │ {os_info} │ {status} │")
        
    print("  └──────────────────────────┴──────────────────┴──────────────────┴─────────────────────────────────┴───────────────┘")
    
    # Scan History
    print("\n📊 Scan History:")
    
    for scan in list(platform.scans.values())[:5]:
        duration = ""
        if scan.started_at and scan.completed_at:
            dur_sec = (scan.completed_at - scan.started_at).total_seconds()
            duration = f"{dur_sec:.1f}s"
        status_icon = "✓" if scan.status == ScanStatus.COMPLETED else "⏳"
        print(f"  {status_icon} {scan.name}: {scan.assets_found} assets ({scan.new_assets} new) [{duration}]")
        
    # Cloud Summary
    print("\n☁️ Cloud Instances:")
    
    cloud_summary = {}
    for asset in platform.assets.values():
        if asset.cloud_provider:
            key = f"{asset.cloud_provider.value}/{asset.cloud_region}"
            cloud_summary[key] = cloud_summary.get(key, 0) + 1
            
    for location, count in sorted(cloud_summary.items()):
        bar = "█" * min(count, 20)
        print(f"  {location:25s} │ {bar} ({count})")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Asset Distribution:")
    
    # By Type
    print("\n  By Type:")
    for atype, count in stats["by_type"].items():
        if count > 0:
            bar = "█" * min(count, 25)
            print(f"    {atype:20s} │ {bar} ({count})")
            
    # By Status
    print("\n  By Status:")
    for status, count in stats["by_status"].items():
        if count > 0:
            bar = "█" * min(count, 25)
            print(f"    {status:15s} │ {bar} ({count})")
            
    # By OS
    print("\n  By Operating System:")
    for os_name, count in sorted(stats["os_distribution"].items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 25)
        print(f"    {os_name[:20]:20s} │ {bar} ({count})")
        
    # By Discovery Method
    print("\n  By Discovery Method:")
    for method, count in stats["by_discovery_method"].items():
        if count > 0:
            bar = "█" * min(count, 25)
            print(f"    {method:15s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Asset Discovery Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Assets:                  {stats['total_assets']:>12}                      │")
    print(f"│ Active Assets:                 {metrics.active_assets:>12}                      │")
    print(f"│ New (24h):                     {metrics.new_assets_24h:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cloud Instances:               {metrics.cloud_instances:>12}                      │")
    print(f"│ Cloud Connections:             {stats['cloud_connections']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Scan Ranges:                   {stats['scan_ranges']:>12}                      │")
    print(f"│ Total Scans:                   {stats['total_scans']:>12}                      │")
    print(f"│ Scans (24h):                   {metrics.scans_completed_24h:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Discovery Schedules:           {stats['schedules']:>12}                      │")
    print(f"│ Credentials:                   {stats['credentials']:>12}                      │")
    print(f"│ Avg Scan Duration:             {metrics.average_scan_duration_sec:>11.1f}s                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Asset Discovery Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
