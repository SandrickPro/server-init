#!/usr/bin/env python3
"""
Server Init - Iteration 330: Multi-Cloud Manager Platform
Платформа управления мультиоблачной инфраструктурой

Функционал:
- Cloud Provider Integration - интеграция облачных провайдеров
- Resource Management - управление ресурсами
- Cross-Cloud Networking - межоблачные сети
- Unified Monitoring - единый мониторинг
- Cost Aggregation - агрегация затрат
- Workload Placement - размещение нагрузок
- Disaster Recovery - аварийное восстановление
- Compliance Management - управление соответствием
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class CloudProvider(Enum):
    """Облачный провайдер"""
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    ALIBABA = "Alibaba Cloud"
    ORACLE = "Oracle Cloud"
    IBM = "IBM Cloud"
    DIGITAL_OCEAN = "DigitalOcean"
    PRIVATE = "Private Cloud"


class ResourceType(Enum):
    """Тип ресурса"""
    VM = "virtual_machine"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    LOAD_BALANCER = "load_balancer"
    SERVERLESS = "serverless"


class ResourceStatus(Enum):
    """Статус ресурса"""
    RUNNING = "running"
    STOPPED = "stopped"
    PENDING = "pending"
    FAILED = "failed"
    TERMINATED = "terminated"


class ConnectionStatus(Enum):
    """Статус подключения"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class PlacementStrategy(Enum):
    """Стратегия размещения"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COMPLIANCE_OPTIMIZED = "compliance_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    AVAILABILITY_OPTIMIZED = "availability_optimized"


class DRStrategy(Enum):
    """Стратегия DR"""
    ACTIVE_ACTIVE = "active_active"
    ACTIVE_PASSIVE = "active_passive"
    PILOT_LIGHT = "pilot_light"
    WARM_STANDBY = "warm_standby"
    BACKUP_RESTORE = "backup_restore"


@dataclass
class CloudAccount:
    """Облачный аккаунт"""
    account_id: str
    name: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    
    # Credentials (simplified)
    credential_type: str = "access_key"  # access_key, service_principal, service_account
    credential_id: str = ""
    
    # Regions
    enabled_regions: List[str] = field(default_factory=list)
    default_region: str = ""
    
    # Status
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    last_sync: datetime = field(default_factory=datetime.now)
    
    # Limits
    resource_quota: Dict[str, int] = field(default_factory=dict)
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CloudResource:
    """Облачный ресурс"""
    resource_id: str
    name: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    account_id: str = ""
    
    # Type
    resource_type: ResourceType = ResourceType.VM
    
    # Location
    region: str = ""
    availability_zone: str = ""
    
    # Native ID
    native_id: str = ""  # AWS: i-xxx, Azure: /subscriptions/xxx
    
    # Configuration
    size: str = ""  # e.g., m5.large, Standard_D2s_v3
    cpu_cores: int = 0
    memory_gb: float = 0.0
    storage_gb: float = 0.0
    
    # Networking
    private_ip: str = ""
    public_ip: str = ""
    vpc_id: str = ""
    subnet_id: str = ""
    
    # Status
    status: ResourceStatus = ResourceStatus.RUNNING
    
    # Cost
    hourly_cost: float = 0.0
    monthly_cost: float = 0.0
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class CrossCloudNetwork:
    """Межоблачная сеть"""
    network_id: str
    name: str
    
    # Endpoints
    endpoints: List[Dict[str, str]] = field(default_factory=list)
    # Each endpoint: {provider, account_id, vpc_id, region, cidr}
    
    # Connection type
    connection_type: str = "vpn"  # vpn, direct_connect, peering, transit_gateway
    
    # Status
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    
    # Bandwidth
    bandwidth_mbps: int = 1000
    
    # Encryption
    encryption_enabled: bool = True
    encryption_protocol: str = "IPSec"
    
    # Routing
    routing_type: str = "dynamic"  # static, dynamic (BGP)
    bgp_asn: int = 0
    
    # Latency
    latency_ms: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkloadPlacement:
    """Размещение нагрузки"""
    placement_id: str
    workload_name: str
    
    # Strategy
    strategy: PlacementStrategy = PlacementStrategy.COST_OPTIMIZED
    
    # Requirements
    cpu_required: int = 0
    memory_required_gb: float = 0.0
    storage_required_gb: float = 0.0
    
    # Constraints
    required_providers: List[CloudProvider] = field(default_factory=list)
    excluded_providers: List[CloudProvider] = field(default_factory=list)
    required_regions: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Placement decision
    selected_provider: Optional[CloudProvider] = None
    selected_region: str = ""
    selected_size: str = ""
    
    # Score
    placement_score: float = 0.0
    cost_score: float = 0.0
    performance_score: float = 0.0
    compliance_score: float = 0.0
    
    # Status
    status: str = "pending"  # pending, placed, failed
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DRConfiguration:
    """Конфигурация DR"""
    dr_id: str
    name: str
    
    # Strategy
    strategy: DRStrategy = DRStrategy.ACTIVE_PASSIVE
    
    # Primary site
    primary_provider: CloudProvider = CloudProvider.AWS
    primary_region: str = ""
    primary_resources: List[str] = field(default_factory=list)
    
    # DR site
    dr_provider: CloudProvider = CloudProvider.AZURE
    dr_region: str = ""
    dr_resources: List[str] = field(default_factory=list)
    
    # RPO/RTO
    rpo_minutes: int = 15
    rto_minutes: int = 60
    
    # Replication
    replication_enabled: bool = True
    replication_frequency_minutes: int = 5
    last_replication: Optional[datetime] = None
    
    # Failover
    auto_failover: bool = False
    failover_threshold: int = 3  # Consecutive failures
    
    # Status
    status: str = "active"  # active, failover, testing
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostSummary:
    """Сводка затрат"""
    summary_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Total
    total_cost: float = 0.0
    currency: str = "USD"
    
    # By provider
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    
    # By resource type
    cost_by_type: Dict[str, float] = field(default_factory=dict)
    
    # By region
    cost_by_region: Dict[str, float] = field(default_factory=dict)
    
    # By tag
    cost_by_tag: Dict[str, float] = field(default_factory=dict)
    
    # Trends
    previous_period_cost: float = 0.0
    cost_change_percent: float = 0.0
    
    # Forecast
    forecasted_cost: float = 0.0
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceCheck:
    """Проверка соответствия"""
    check_id: str
    
    # Resource
    resource_id: str = ""
    provider: CloudProvider = CloudProvider.AWS
    
    # Framework
    framework: str = ""  # SOC2, HIPAA, GDPR, PCI-DSS
    control_id: str = ""
    
    # Status
    status: str = "compliant"  # compliant, non_compliant, not_applicable
    
    # Details
    description: str = ""
    finding: str = ""
    recommendation: str = ""
    
    # Severity
    severity: str = "info"  # info, low, medium, high, critical
    
    # Timestamps
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class HealthStatus:
    """Статус здоровья"""
    health_id: str
    
    # Provider
    provider: CloudProvider = CloudProvider.AWS
    account_id: str = ""
    region: str = ""
    
    # Metrics
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    network_throughput_mbps: float = 0.0
    error_rate: float = 0.0
    
    # Status
    overall_status: str = "healthy"  # healthy, degraded, unhealthy
    
    # Issues
    active_issues: List[str] = field(default_factory=list)
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class MultiCloudManager:
    """Менеджер мультиоблачной инфраструктуры"""
    
    def __init__(self):
        self.accounts: Dict[str, CloudAccount] = {}
        self.resources: Dict[str, CloudResource] = {}
        self.networks: Dict[str, CrossCloudNetwork] = {}
        self.placements: Dict[str, WorkloadPlacement] = {}
        self.dr_configs: Dict[str, DRConfiguration] = {}
        self.cost_summaries: Dict[str, CostSummary] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.health_statuses: Dict[str, HealthStatus] = {}
        
    async def add_cloud_account(self, name: str,
                               provider: CloudProvider,
                               credential_type: str,
                               credential_id: str,
                               regions: List[str],
                               default_region: str = "") -> CloudAccount:
        """Добавление облачного аккаунта"""
        account = CloudAccount(
            account_id=f"acc_{uuid.uuid4().hex[:8]}",
            name=name,
            provider=provider,
            credential_type=credential_type,
            credential_id=credential_id,
            enabled_regions=regions,
            default_region=default_region or (regions[0] if regions else "")
        )
        
        self.accounts[account.account_id] = account
        return account
        
    async def sync_account(self, account_id: str) -> bool:
        """Синхронизация аккаунта"""
        account = self.accounts.get(account_id)
        if not account:
            return False
            
        account.last_sync = datetime.now()
        account.status = ConnectionStatus.CONNECTED
        
        return True
        
    async def add_resource(self, name: str,
                          provider: CloudProvider,
                          account_id: str,
                          resource_type: ResourceType,
                          region: str,
                          native_id: str,
                          size: str = "",
                          cpu_cores: int = 0,
                          memory_gb: float = 0.0,
                          storage_gb: float = 0.0,
                          hourly_cost: float = 0.0,
                          tags: Dict[str, str] = None) -> CloudResource:
        """Добавление ресурса"""
        resource = CloudResource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            provider=provider,
            account_id=account_id,
            resource_type=resource_type,
            region=region,
            native_id=native_id,
            size=size,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            storage_gb=storage_gb,
            hourly_cost=hourly_cost,
            monthly_cost=hourly_cost * 730,
            private_ip=f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            tags=tags or {}
        )
        
        self.resources[resource.resource_id] = resource
        return resource
        
    async def start_resource(self, resource_id: str) -> bool:
        """Запуск ресурса"""
        resource = self.resources.get(resource_id)
        if not resource:
            return False
            
        if resource.status in [ResourceStatus.STOPPED, ResourceStatus.PENDING]:
            resource.status = ResourceStatus.RUNNING
            resource.last_updated = datetime.now()
            return True
            
        return False
        
    async def stop_resource(self, resource_id: str) -> bool:
        """Остановка ресурса"""
        resource = self.resources.get(resource_id)
        if not resource:
            return False
            
        if resource.status == ResourceStatus.RUNNING:
            resource.status = ResourceStatus.STOPPED
            resource.last_updated = datetime.now()
            return True
            
        return False
        
    async def create_cross_cloud_network(self, name: str,
                                        endpoints: List[Dict[str, str]],
                                        connection_type: str = "vpn",
                                        bandwidth_mbps: int = 1000) -> CrossCloudNetwork:
        """Создание межоблачной сети"""
        network = CrossCloudNetwork(
            network_id=f"net_{uuid.uuid4().hex[:8]}",
            name=name,
            endpoints=endpoints,
            connection_type=connection_type,
            bandwidth_mbps=bandwidth_mbps,
            latency_ms=random.uniform(5, 50)
        )
        
        self.networks[network.network_id] = network
        return network
        
    async def plan_workload_placement(self, workload_name: str,
                                     strategy: PlacementStrategy,
                                     cpu_required: int,
                                     memory_required_gb: float,
                                     storage_required_gb: float = 0,
                                     required_providers: List[CloudProvider] = None,
                                     compliance_requirements: List[str] = None) -> WorkloadPlacement:
        """Планирование размещения нагрузки"""
        placement = WorkloadPlacement(
            placement_id=f"plc_{uuid.uuid4().hex[:8]}",
            workload_name=workload_name,
            strategy=strategy,
            cpu_required=cpu_required,
            memory_required_gb=memory_required_gb,
            storage_required_gb=storage_required_gb,
            required_providers=required_providers or [],
            compliance_requirements=compliance_requirements or []
        )
        
        # Calculate placement decision
        await self._calculate_placement(placement)
        
        self.placements[placement.placement_id] = placement
        return placement
        
    async def _calculate_placement(self, placement: WorkloadPlacement):
        """Расчёт размещения"""
        # Get available providers
        providers = placement.required_providers or list(CloudProvider)
        providers = [p for p in providers if p not in placement.excluded_providers]
        
        if not providers:
            placement.status = "failed"
            return
            
        # Score each provider based on strategy
        best_provider = None
        best_score = -1
        best_region = ""
        
        for provider in providers:
            accounts = [a for a in self.accounts.values() if a.provider == provider]
            if not accounts:
                continue
                
            for account in accounts:
                for region in account.enabled_regions:
                    score = self._calculate_provider_score(
                        provider, region, placement.strategy
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_provider = provider
                        best_region = region
                        
        if best_provider:
            placement.selected_provider = best_provider
            placement.selected_region = best_region
            placement.placement_score = best_score
            placement.status = "placed"
            
            # Set size based on requirements
            placement.selected_size = self._get_instance_size(
                best_provider, placement.cpu_required, placement.memory_required_gb
            )
        else:
            placement.status = "failed"
            
    def _calculate_provider_score(self, provider: CloudProvider,
                                  region: str,
                                  strategy: PlacementStrategy) -> float:
        """Расчёт оценки провайдера"""
        base_score = 50.0
        
        # Strategy-specific adjustments
        if strategy == PlacementStrategy.COST_OPTIMIZED:
            cost_factors = {CloudProvider.AWS: 0.9, CloudProvider.GCP: 0.85, CloudProvider.AZURE: 0.95}
            base_score += (1 - cost_factors.get(provider, 1.0)) * 30
            
        elif strategy == PlacementStrategy.PERFORMANCE_OPTIMIZED:
            perf_factors = {CloudProvider.AWS: 0.95, CloudProvider.GCP: 0.9, CloudProvider.AZURE: 0.9}
            base_score += perf_factors.get(provider, 0.8) * 30
            
        elif strategy == PlacementStrategy.COMPLIANCE_OPTIMIZED:
            compliance_factors = {CloudProvider.AWS: 0.95, CloudProvider.AZURE: 0.95, CloudProvider.GCP: 0.9}
            base_score += compliance_factors.get(provider, 0.7) * 30
            
        # Add some randomness
        base_score += random.uniform(-5, 5)
        
        return min(100, max(0, base_score))
        
    def _get_instance_size(self, provider: CloudProvider,
                          cpu: int, memory_gb: float) -> str:
        """Получение размера инстанса"""
        sizes = {
            CloudProvider.AWS: {
                (2, 4): "t3.medium",
                (4, 8): "t3.large",
                (4, 16): "m5.xlarge",
                (8, 32): "m5.2xlarge",
                (16, 64): "m5.4xlarge"
            },
            CloudProvider.AZURE: {
                (2, 4): "Standard_B2s",
                (4, 8): "Standard_D2s_v3",
                (4, 16): "Standard_D4s_v3",
                (8, 32): "Standard_D8s_v3",
                (16, 64): "Standard_D16s_v3"
            },
            CloudProvider.GCP: {
                (2, 4): "e2-medium",
                (4, 8): "e2-standard-4",
                (4, 16): "n2-standard-4",
                (8, 32): "n2-standard-8",
                (16, 64): "n2-standard-16"
            }
        }
        
        provider_sizes = sizes.get(provider, {})
        for (c, m), size in provider_sizes.items():
            if cpu <= c and memory_gb <= m:
                return size
                
        return "custom"
        
    async def configure_dr(self, name: str,
                          strategy: DRStrategy,
                          primary_provider: CloudProvider,
                          primary_region: str,
                          dr_provider: CloudProvider,
                          dr_region: str,
                          rpo_minutes: int = 15,
                          rto_minutes: int = 60) -> DRConfiguration:
        """Конфигурация DR"""
        dr_config = DRConfiguration(
            dr_id=f"dr_{uuid.uuid4().hex[:8]}",
            name=name,
            strategy=strategy,
            primary_provider=primary_provider,
            primary_region=primary_region,
            dr_provider=dr_provider,
            dr_region=dr_region,
            rpo_minutes=rpo_minutes,
            rto_minutes=rto_minutes,
            replication_frequency_minutes=rpo_minutes // 3
        )
        
        # Add primary resources
        primary_resources = [r.resource_id for r in self.resources.values()
                           if r.provider == primary_provider and r.region == primary_region]
        dr_config.primary_resources = primary_resources[:10]
        
        self.dr_configs[dr_config.dr_id] = dr_config
        return dr_config
        
    async def trigger_dr_failover(self, dr_id: str) -> bool:
        """Инициация DR failover"""
        dr_config = self.dr_configs.get(dr_id)
        if not dr_config:
            return False
            
        dr_config.status = "failover"
        
        # In real implementation: switch DNS, promote replicas, etc.
        
        return True
        
    async def run_compliance_check(self, resource_id: str,
                                  framework: str) -> List[ComplianceCheck]:
        """Запуск проверки соответствия"""
        resource = self.resources.get(resource_id)
        if not resource:
            return []
            
        checks = []
        
        # Simulate compliance checks
        controls = {
            "SOC2": ["CC6.1", "CC6.7", "CC7.2"],
            "HIPAA": ["164.312(a)", "164.312(e)"],
            "PCI-DSS": ["1.1", "2.2", "3.4"],
            "GDPR": ["Art.25", "Art.32"]
        }
        
        for control_id in controls.get(framework, []):
            status = random.choice(["compliant", "compliant", "compliant", "non_compliant"])
            severity = "info" if status == "compliant" else random.choice(["medium", "high"])
            
            check = ComplianceCheck(
                check_id=f"chk_{uuid.uuid4().hex[:8]}",
                resource_id=resource_id,
                provider=resource.provider,
                framework=framework,
                control_id=control_id,
                status=status,
                description=f"Compliance check for {framework} {control_id}",
                finding="" if status == "compliant" else f"Non-compliant: {control_id}",
                recommendation="" if status == "compliant" else f"Implement control {control_id}",
                severity=severity
            )
            
            checks.append(check)
            self.compliance_checks[check.check_id] = check
            
        return checks
        
    async def collect_health_status(self, account_id: str) -> Optional[HealthStatus]:
        """Сбор статуса здоровья"""
        account = self.accounts.get(account_id)
        if not account:
            return None
            
        # Calculate metrics from resources
        account_resources = [r for r in self.resources.values() if r.account_id == account_id]
        
        cpu_util = random.uniform(20, 80)
        mem_util = random.uniform(30, 70)
        net_throughput = random.uniform(100, 1000)
        error_rate = random.uniform(0, 2)
        
        overall = "healthy"
        if cpu_util > 80 or mem_util > 80 or error_rate > 1:
            overall = "degraded"
        if error_rate > 5:
            overall = "unhealthy"
            
        issues = []
        if cpu_util > 80:
            issues.append("High CPU utilization")
        if mem_util > 80:
            issues.append("High memory utilization")
        if error_rate > 1:
            issues.append("Elevated error rate")
            
        health = HealthStatus(
            health_id=f"health_{uuid.uuid4().hex[:8]}",
            provider=account.provider,
            account_id=account_id,
            region=account.default_region,
            cpu_utilization=cpu_util,
            memory_utilization=mem_util,
            network_throughput_mbps=net_throughput,
            error_rate=error_rate,
            overall_status=overall,
            active_issues=issues
        )
        
        self.health_statuses[health.health_id] = health
        return health
        
    async def generate_cost_summary(self, period_days: int = 30) -> CostSummary:
        """Генерация сводки затрат"""
        summary = CostSummary(
            summary_id=f"cost_{uuid.uuid4().hex[:8]}",
            period_start=datetime.now() - timedelta(days=period_days),
            period_end=datetime.now()
        )
        
        for resource in self.resources.values():
            if resource.status == ResourceStatus.RUNNING:
                summary.total_cost += resource.monthly_cost
                
                # By provider
                provider_key = resource.provider.value
                summary.cost_by_provider[provider_key] = summary.cost_by_provider.get(provider_key, 0) + resource.monthly_cost
                
                # By type
                type_key = resource.resource_type.value
                summary.cost_by_type[type_key] = summary.cost_by_type.get(type_key, 0) + resource.monthly_cost
                
                # By region
                summary.cost_by_region[resource.region] = summary.cost_by_region.get(resource.region, 0) + resource.monthly_cost
                
        summary.previous_period_cost = summary.total_cost * random.uniform(0.9, 1.1)
        summary.cost_change_percent = ((summary.total_cost - summary.previous_period_cost) / summary.previous_period_cost * 100) if summary.previous_period_cost > 0 else 0
        summary.forecasted_cost = summary.total_cost * 1.05
        
        self.cost_summaries[summary.summary_id] = summary
        return summary
        
    def get_resource_count_by_provider(self) -> Dict[str, int]:
        """Количество ресурсов по провайдерам"""
        by_provider = {}
        for resource in self.resources.values():
            provider = resource.provider.value
            by_provider[provider] = by_provider.get(provider, 0) + 1
        return by_provider
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_accounts = len(self.accounts)
        connected_accounts = sum(1 for a in self.accounts.values() if a.status == ConnectionStatus.CONNECTED)
        
        total_resources = len(self.resources)
        running_resources = sum(1 for r in self.resources.values() if r.status == ResourceStatus.RUNNING)
        
        by_provider = self.get_resource_count_by_provider()
        by_type = {}
        for resource in self.resources.values():
            rtype = resource.resource_type.value
            by_type[rtype] = by_type.get(rtype, 0) + 1
            
        total_cost = sum(r.monthly_cost for r in self.resources.values() if r.status == ResourceStatus.RUNNING)
        
        total_networks = len(self.networks)
        active_networks = sum(1 for n in self.networks.values() if n.status == ConnectionStatus.CONNECTED)
        
        return {
            "total_accounts": total_accounts,
            "connected_accounts": connected_accounts,
            "total_resources": total_resources,
            "running_resources": running_resources,
            "resources_by_provider": by_provider,
            "resources_by_type": by_type,
            "total_monthly_cost": total_cost,
            "total_networks": total_networks,
            "active_networks": active_networks,
            "total_dr_configs": len(self.dr_configs),
            "total_placements": len(self.placements),
            "compliance_checks": len(self.compliance_checks)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 330: Multi-Cloud Manager Platform")
    print("=" * 60)
    
    mcm = MultiCloudManager()
    print("✓ Multi-Cloud Manager created")
    
    # Add cloud accounts
    print("\n☁️ Adding Cloud Accounts...")
    
    accounts_data = [
        ("AWS Production", CloudProvider.AWS, "access_key", "AKIA...", ["us-east-1", "us-west-2", "eu-west-1"]),
        ("AWS Development", CloudProvider.AWS, "access_key", "AKIA...", ["us-east-1", "us-west-2"]),
        ("Azure Enterprise", CloudProvider.AZURE, "service_principal", "app-id...", ["eastus", "westus2", "westeurope"]),
        ("GCP Platform", CloudProvider.GCP, "service_account", "project@...", ["us-central1", "europe-west1", "asia-east1"]),
        ("Private DC", CloudProvider.PRIVATE, "access_key", "local...", ["dc1", "dc2"])
    ]
    
    accounts = []
    for name, provider, cred_type, cred_id, regions in accounts_data:
        account = await mcm.add_cloud_account(name, provider, cred_type, cred_id, regions)
        accounts.append(account)
        await mcm.sync_account(account.account_id)
        print(f"  ☁️ {name} ({provider.value})")
        
    # Add resources
    print("\n🖥️ Adding Cloud Resources...")
    
    resources_data = [
        # AWS
        ("web-server-1", CloudProvider.AWS, "us-east-1", "i-abc123", "m5.xlarge", 4, 16, 100, 0.192),
        ("web-server-2", CloudProvider.AWS, "us-east-1", "i-abc124", "m5.xlarge", 4, 16, 100, 0.192),
        ("api-server-1", CloudProvider.AWS, "us-east-1", "i-def456", "c5.2xlarge", 8, 16, 50, 0.34),
        ("db-primary", CloudProvider.AWS, "us-east-1", "i-ghi789", "r5.2xlarge", 8, 64, 500, 0.504),
        ("cache-server", CloudProvider.AWS, "us-west-2", "i-jkl012", "r5.large", 2, 16, 50, 0.126),
        # Azure
        ("app-server-1", CloudProvider.AZURE, "eastus", "/subs/.../vm1", "Standard_D4s_v3", 4, 16, 100, 0.192),
        ("app-server-2", CloudProvider.AZURE, "eastus", "/subs/.../vm2", "Standard_D4s_v3", 4, 16, 100, 0.192),
        ("analytics-server", CloudProvider.AZURE, "westeurope", "/subs/.../vm3", "Standard_D8s_v3", 8, 32, 200, 0.384),
        # GCP
        ("ml-server-1", CloudProvider.GCP, "us-central1", "ml-vm-1", "n2-standard-8", 8, 32, 100, 0.38),
        ("ml-server-2", CloudProvider.GCP, "us-central1", "ml-vm-2", "n2-standard-8", 8, 32, 100, 0.38),
        # Private
        ("legacy-app", CloudProvider.PRIVATE, "dc1", "vm-001", "large", 8, 32, 500, 0.10)
    ]
    
    resources = []
    for name, provider, region, native_id, size, cpu, mem, storage, cost in resources_data:
        account = next((a for a in accounts if a.provider == provider), accounts[0])
        resource = await mcm.add_resource(
            name, provider, account.account_id, ResourceType.VM, region,
            native_id, size, cpu, mem, storage, cost,
            {"environment": random.choice(["production", "development", "staging"])}
        )
        resources.append(resource)
        
    print(f"  ✓ Added {len(resources)} resources")
    
    # Create cross-cloud networks
    print("\n🌐 Creating Cross-Cloud Networks...")
    
    networks_data = [
        ("AWS-Azure VPN", [
            {"provider": "AWS", "vpc_id": "vpc-123", "region": "us-east-1", "cidr": "10.0.0.0/16"},
            {"provider": "Azure", "vpc_id": "vnet-456", "region": "eastus", "cidr": "10.1.0.0/16"}
        ], "vpn", 1000),
        ("AWS-GCP Direct", [
            {"provider": "AWS", "vpc_id": "vpc-123", "region": "us-east-1", "cidr": "10.0.0.0/16"},
            {"provider": "GCP", "vpc_id": "vpc-789", "region": "us-central1", "cidr": "10.2.0.0/16"}
        ], "direct_connect", 10000),
        ("AWS-Private Transit", [
            {"provider": "AWS", "vpc_id": "vpc-123", "region": "us-east-1", "cidr": "10.0.0.0/16"},
            {"provider": "Private", "vpc_id": "dc-vlan-100", "region": "dc1", "cidr": "192.168.0.0/16"}
        ], "transit_gateway", 5000)
    ]
    
    networks = []
    for name, endpoints, conn_type, bandwidth in networks_data:
        network = await mcm.create_cross_cloud_network(name, endpoints, conn_type, bandwidth)
        networks.append(network)
        print(f"  🌐 {name} ({conn_type})")
        
    # Plan workload placements
    print("\n📍 Planning Workload Placements...")
    
    placements_data = [
        ("New Web Service", PlacementStrategy.COST_OPTIMIZED, 4, 8, 50, [CloudProvider.AWS, CloudProvider.GCP]),
        ("ML Training Pipeline", PlacementStrategy.PERFORMANCE_OPTIMIZED, 16, 64, 500, [CloudProvider.GCP]),
        ("Healthcare App", PlacementStrategy.COMPLIANCE_OPTIMIZED, 8, 32, 100, [CloudProvider.AWS, CloudProvider.AZURE]),
        ("Global API", PlacementStrategy.LATENCY_OPTIMIZED, 4, 16, 50, []),
        ("Critical Database", PlacementStrategy.AVAILABILITY_OPTIMIZED, 8, 64, 1000, [CloudProvider.AWS])
    ]
    
    placements = []
    for name, strategy, cpu, mem, storage, providers in placements_data:
        compliance = ["HIPAA"] if "Healthcare" in name else []
        placement = await mcm.plan_workload_placement(
            name, strategy, cpu, mem, storage, providers, compliance
        )
        placements.append(placement)
        status_icon = "✓" if placement.status == "placed" else "✗"
        print(f"  {status_icon} {name} -> {placement.selected_provider.value if placement.selected_provider else 'N/A'}")
        
    # Configure DR
    print("\n🔄 Configuring Disaster Recovery...")
    
    dr_configs_data = [
        ("Production DR", DRStrategy.ACTIVE_PASSIVE, CloudProvider.AWS, "us-east-1", CloudProvider.AZURE, "westus2", 15, 60),
        ("Database DR", DRStrategy.WARM_STANDBY, CloudProvider.AWS, "us-east-1", CloudProvider.AWS, "us-west-2", 5, 30),
        ("Analytics DR", DRStrategy.BACKUP_RESTORE, CloudProvider.GCP, "us-central1", CloudProvider.AWS, "us-east-1", 60, 240)
    ]
    
    dr_configs = []
    for name, strategy, pri_prov, pri_reg, dr_prov, dr_reg, rpo, rto in dr_configs_data:
        dr_config = await mcm.configure_dr(name, strategy, pri_prov, pri_reg, dr_prov, dr_reg, rpo, rto)
        dr_configs.append(dr_config)
        print(f"  🔄 {name}: {pri_prov.value} -> {dr_prov.value}")
        
    # Run compliance checks
    print("\n✅ Running Compliance Checks...")
    
    all_checks = []
    for resource in resources[:5]:
        checks = await mcm.run_compliance_check(resource.resource_id, "SOC2")
        all_checks.extend(checks)
        
    compliant = sum(1 for c in all_checks if c.status == "compliant")
    print(f"  ✓ {len(all_checks)} checks completed: {compliant} compliant")
    
    # Collect health status
    print("\n❤️ Collecting Health Status...")
    
    health_statuses = []
    for account in accounts:
        health = await mcm.collect_health_status(account.account_id)
        if health:
            health_statuses.append(health)
            
    healthy = sum(1 for h in health_statuses if h.overall_status == "healthy")
    print(f"  ✓ {len(health_statuses)} accounts checked: {healthy} healthy")
    
    # Generate cost summary
    print("\n💰 Generating Cost Summary...")
    
    cost_summary = await mcm.generate_cost_summary(30)
    print(f"  ✓ Total monthly cost: ${cost_summary.total_cost:,.2f}")
    
    # Cloud accounts
    print("\n☁️ Cloud Accounts:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Account Name           │ Provider      │ Regions   │ Status      │ Last Sync            │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for account in accounts:
        name = account.name[:22].ljust(22)
        provider = account.provider.value[:13].ljust(13)
        regions = str(len(account.enabled_regions)).ljust(9)
        
        status_icon = "✓" if account.status == ConnectionStatus.CONNECTED else "✗"
        status = f"{status_icon} {account.status.value}"[:11].ljust(11)
        
        last_sync = account.last_sync.strftime("%Y-%m-%d %H:%M")[:20].ljust(20)
        
        print(f"  │ {name} │ {provider} │ {regions} │ {status} │ {last_sync} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Resources by provider
    print("\n🖥️ Resources by Provider:")
    
    stats = mcm.get_statistics()
    total = stats['total_resources']
    
    for provider, count in sorted(stats['resources_by_provider'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        bar_len = int(pct / 2.5)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {provider:15} [{bar}] {count} ({pct:.1f}%)")
        
    # Cost by provider
    print("\n💰 Cost by Provider:")
    
    total_cost = cost_summary.total_cost
    for provider, cost in sorted(cost_summary.cost_by_provider.items(), key=lambda x: x[1], reverse=True):
        pct = (cost / total_cost * 100) if total_cost > 0 else 0
        bar_len = int(pct / 2.5)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {provider:15} [{bar}] ${cost:,.0f} ({pct:.1f}%)")
        
    # Cross-cloud networks
    print("\n🌐 Cross-Cloud Networks:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Network Name           │ Type           │ Bandwidth   │ Latency   │ Status              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for network in networks:
        name = network.name[:22].ljust(22)
        conn_type = network.connection_type[:14].ljust(14)
        bandwidth = f"{network.bandwidth_mbps} Mbps".ljust(11)
        latency = f"{network.latency_ms:.1f} ms".ljust(9)
        
        status_icon = "✓" if network.status == ConnectionStatus.CONNECTED else "✗"
        status = f"{status_icon} {network.status.value}"[:19].ljust(19)
        
        print(f"  │ {name} │ {conn_type} │ {bandwidth} │ {latency} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Workload placements
    print("\n📍 Workload Placements:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Workload                │ Strategy             │ Provider      │ Region       │ Size           │ Score      │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for placement in placements:
        name = placement.workload_name[:23].ljust(23)
        strategy = placement.strategy.value[:20].ljust(20)
        provider = (placement.selected_provider.value if placement.selected_provider else "N/A")[:13].ljust(13)
        region = placement.selected_region[:12].ljust(12)
        size = placement.selected_size[:14].ljust(14)
        score = f"{placement.placement_score:.1f}%".ljust(10)
        
        print(f"  │ {name} │ {strategy} │ {provider} │ {region} │ {size} │ {score} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # DR configurations
    print("\n🔄 DR Configurations:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                 │ Strategy        │ Primary           │ DR Site           │ RPO     │ RTO     │ Status │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for dr in dr_configs:
        name = dr.name[:20].ljust(20)
        strategy = dr.strategy.value[:15].ljust(15)
        primary = f"{dr.primary_provider.value}/{dr.primary_region}"[:17].ljust(17)
        dr_site = f"{dr.dr_provider.value}/{dr.dr_region}"[:17].ljust(17)
        rpo = f"{dr.rpo_minutes}m".ljust(7)
        rto = f"{dr.rto_minutes}m".ljust(7)
        status = dr.status[:6].ljust(6)
        
        print(f"  │ {name} │ {strategy} │ {primary} │ {dr_site} │ {rpo} │ {rto} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Health status
    print("\n❤️ Health Status:")
    
    for health in health_statuses:
        status_icon = {"healthy": "✓", "degraded": "⚠", "unhealthy": "✗"}.get(health.overall_status, "?")
        print(f"\n  {status_icon} {health.provider.value} ({health.region})")
        print(f"    CPU: {health.cpu_utilization:.1f}% | Memory: {health.memory_utilization:.1f}%")
        print(f"    Network: {health.network_throughput_mbps:.0f} Mbps | Errors: {health.error_rate:.2f}%")
        if health.active_issues:
            print(f"    Issues: {', '.join(health.active_issues)}")
            
    # Compliance summary
    print("\n✅ Compliance Summary:")
    
    compliant_count = sum(1 for c in all_checks if c.status == "compliant")
    non_compliant_count = sum(1 for c in all_checks if c.status == "non_compliant")
    
    print(f"\n  Total Checks: {len(all_checks)}")
    print(f"  Compliant: {compliant_count} ({compliant_count/len(all_checks)*100:.1f}%)")
    print(f"  Non-Compliant: {non_compliant_count}")
    
    # Overall statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Cloud Accounts: {stats['connected_accounts']}/{stats['total_accounts']} connected")
    print(f"  Resources: {stats['running_resources']}/{stats['total_resources']} running")
    print(f"  Networks: {stats['active_networks']}/{stats['total_networks']} active")
    print(f"  DR Configs: {stats['total_dr_configs']}")
    print(f"  Monthly Cost: ${stats['total_monthly_cost']:,.2f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Multi-Cloud Manager Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cloud Accounts:               {stats['connected_accounts']:>12} connected            │")
    print(f"│ Total Resources:              {stats['total_resources']:>12}                      │")
    print(f"│ Running Resources:            {stats['running_resources']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Cross-Cloud Networks:         {stats['active_networks']:>12} active               │")
    print(f"│ DR Configurations:            {stats['total_dr_configs']:>12}                      │")
    print(f"│ Total Monthly Cost:           ${stats['total_monthly_cost']:>11,.2f}                  │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Multi-Cloud Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
