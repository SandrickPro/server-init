#!/usr/bin/env python3
"""
Server Init - Iteration 218: Environment Manager Platform
Платформа управления окружениями

Функционал:
- Environment Provisioning - провижининг окружений
- Configuration Management - управление конфигурацией
- Environment Promotion - продвижение между окружениями
- Secret Injection - инъекция секретов
- Resource Allocation - выделение ресурсов
- Environment Cloning - клонирование окружений
- Lifecycle Management - управление жизненным циклом
- Cost Tracking - отслеживание затрат
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class EnvironmentType(Enum):
    """Тип окружения"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    PREVIEW = "preview"
    SANDBOX = "sandbox"


class EnvironmentStatus(Enum):
    """Статус окружения"""
    PROVISIONING = "provisioning"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class PromotionStatus(Enum):
    """Статус продвижения"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResourceTier(Enum):
    """Уровень ресурсов"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PRODUCTION = "production"


@dataclass
class ResourceSpec:
    """Спецификация ресурсов"""
    cpu_cores: int = 2
    memory_gb: int = 4
    storage_gb: int = 50
    replicas: int = 1
    
    # Networking
    public_access: bool = False
    load_balancer: bool = False
    
    # Database
    database_size_gb: int = 10


@dataclass
class EnvironmentConfig:
    """Конфигурация окружения"""
    config_id: str
    name: str = ""
    
    # Config values
    values: Dict[str, Any] = field(default_factory=dict)
    
    # Secrets (references)
    secrets: List[str] = field(default_factory=list)
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Version
    version: int = 1


@dataclass
class Environment:
    """Окружение"""
    env_id: str
    name: str = ""
    
    # Type
    env_type: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    # Status
    status: EnvironmentStatus = EnvironmentStatus.PROVISIONING
    
    # Resources
    resource_spec: ResourceSpec = field(default_factory=ResourceSpec)
    resource_tier: ResourceTier = ResourceTier.STANDARD
    
    # Configuration
    config: Optional[EnvironmentConfig] = None
    
    # Version
    deployed_version: str = ""
    
    # URLs
    url: str = ""
    internal_url: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_deployed: Optional[datetime] = None
    
    # Cost
    hourly_cost: float = 0
    monthly_cost: float = 0
    
    # Owner
    owner: str = ""
    team: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # TTL for ephemeral environments
    ttl_hours: Optional[int] = None
    expires_at: Optional[datetime] = None


@dataclass
class PromotionRequest:
    """Запрос на продвижение"""
    request_id: str
    
    # Source and target
    source_env_id: str = ""
    target_env_type: EnvironmentType = EnvironmentType.STAGING
    
    # Version
    version: str = ""
    
    # Status
    status: PromotionStatus = PromotionStatus.PENDING
    
    # Approval
    requester: str = ""
    approver: Optional[str] = None
    
    # Time
    requested_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Notes
    notes: str = ""


@dataclass
class EnvironmentClone:
    """Клон окружения"""
    clone_id: str
    source_env_id: str = ""
    target_env_id: str = ""
    
    # Options
    include_data: bool = False
    include_secrets: bool = False
    
    # Status
    status: str = "pending"  # pending, cloning, completed, failed
    progress_percent: float = 0
    
    # Time
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class CostReport:
    """Отчёт о затратах"""
    report_id: str
    env_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Costs
    compute_cost: float = 0
    storage_cost: float = 0
    network_cost: float = 0
    database_cost: float = 0
    total_cost: float = 0


class ResourceCalculator:
    """Калькулятор ресурсов"""
    
    TIER_SPECS = {
        ResourceTier.MINIMAL: ResourceSpec(1, 1, 10, 1),
        ResourceTier.STANDARD: ResourceSpec(2, 4, 50, 2),
        ResourceTier.ENHANCED: ResourceSpec(4, 8, 100, 3),
        ResourceTier.PRODUCTION: ResourceSpec(8, 16, 200, 5, True, True, 50),
    }
    
    # Hourly costs per resource
    CPU_COST_HOUR = 0.05
    MEMORY_COST_HOUR = 0.01
    STORAGE_COST_HOUR = 0.001
    
    def get_tier_spec(self, tier: ResourceTier) -> ResourceSpec:
        """Получить спецификацию уровня"""
        return self.TIER_SPECS.get(tier, self.TIER_SPECS[ResourceTier.STANDARD])
        
    def calculate_hourly_cost(self, spec: ResourceSpec) -> float:
        """Расчёт часовой стоимости"""
        cpu_cost = spec.cpu_cores * spec.replicas * self.CPU_COST_HOUR
        memory_cost = spec.memory_gb * spec.replicas * self.MEMORY_COST_HOUR
        storage_cost = spec.storage_gb * self.STORAGE_COST_HOUR
        
        # Additional costs
        lb_cost = 0.025 if spec.load_balancer else 0
        db_cost = spec.database_size_gb * 0.002
        
        return cpu_cost + memory_cost + storage_cost + lb_cost + db_cost


class EnvironmentProvisioner:
    """Провизионер окружений"""
    
    def __init__(self, resource_calculator: ResourceCalculator):
        self.calculator = resource_calculator
        
    async def provision(self, env: Environment) -> bool:
        """Провижининг окружения"""
        env.status = EnvironmentStatus.PROVISIONING
        
        # Simulate provisioning
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Set URLs
        env.url = f"https://{env.name}.{env.env_type.value}.example.com"
        env.internal_url = f"http://{env.name}.internal:8080"
        
        # Calculate costs
        env.hourly_cost = self.calculator.calculate_hourly_cost(env.resource_spec)
        env.monthly_cost = env.hourly_cost * 24 * 30
        
        # Set TTL for ephemeral environments
        if env.env_type == EnvironmentType.PREVIEW:
            env.ttl_hours = 24
            env.expires_at = datetime.now() + timedelta(hours=24)
        elif env.env_type == EnvironmentType.SANDBOX:
            env.ttl_hours = 72
            env.expires_at = datetime.now() + timedelta(hours=72)
            
        env.status = EnvironmentStatus.RUNNING
        env.last_deployed = datetime.now()
        
        return True


class EnvironmentManagerPlatform:
    """Платформа управления окружениями"""
    
    def __init__(self):
        self.environments: Dict[str, Environment] = {}
        self.configs: Dict[str, EnvironmentConfig] = {}
        self.promotions: Dict[str, PromotionRequest] = {}
        self.clones: Dict[str, EnvironmentClone] = {}
        self.cost_reports: List[CostReport] = []
        
        self.calculator = ResourceCalculator()
        self.provisioner = EnvironmentProvisioner(self.calculator)
        
    def create_config(self, name: str, values: Dict[str, Any] = None,
                     feature_flags: Dict[str, bool] = None) -> EnvironmentConfig:
        """Создание конфигурации"""
        config = EnvironmentConfig(
            config_id=f"config_{uuid.uuid4().hex[:8]}",
            name=name,
            values=values or {},
            feature_flags=feature_flags or {}
        )
        self.configs[config.config_id] = config
        return config
        
    async def create_environment(self, name: str,
                                env_type: EnvironmentType,
                                tier: ResourceTier = ResourceTier.STANDARD,
                                config_id: str = "",
                                owner: str = "",
                                team: str = "") -> Environment:
        """Создание окружения"""
        spec = self.calculator.get_tier_spec(tier)
        
        env = Environment(
            env_id=f"env_{uuid.uuid4().hex[:8]}",
            name=name,
            env_type=env_type,
            resource_spec=spec,
            resource_tier=tier,
            config=self.configs.get(config_id),
            owner=owner,
            team=team
        )
        
        self.environments[env.env_id] = env
        
        # Provision
        await self.provisioner.provision(env)
        
        return env
        
    async def deploy_to_environment(self, env_id: str, version: str) -> bool:
        """Деплой в окружение"""
        env = self.environments.get(env_id)
        if not env:
            return False
            
        if env.status != EnvironmentStatus.RUNNING:
            return False
            
        # Simulate deployment
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        env.deployed_version = version
        env.last_deployed = datetime.now()
        env.updated_at = datetime.now()
        
        return True
        
    async def request_promotion(self, source_env_id: str,
                               target_type: EnvironmentType,
                               requester: str,
                               notes: str = "") -> PromotionRequest:
        """Запрос на продвижение"""
        source = self.environments.get(source_env_id)
        
        request = PromotionRequest(
            request_id=f"promo_{uuid.uuid4().hex[:8]}",
            source_env_id=source_env_id,
            target_env_type=target_type,
            version=source.deployed_version if source else "",
            requester=requester,
            notes=notes
        )
        
        self.promotions[request.request_id] = request
        return request
        
    async def approve_promotion(self, request_id: str, approver: str) -> bool:
        """Одобрение продвижения"""
        request = self.promotions.get(request_id)
        if not request or request.status != PromotionStatus.PENDING:
            return False
            
        request.status = PromotionStatus.APPROVED
        request.approver = approver
        request.approved_at = datetime.now()
        
        # Execute promotion
        request.status = PromotionStatus.IN_PROGRESS
        
        # Find target environment of the right type
        target_env = None
        for env in self.environments.values():
            if env.env_type == request.target_env_type:
                target_env = env
                break
                
        if target_env:
            await self.deploy_to_environment(target_env.env_id, request.version)
            
        request.status = PromotionStatus.COMPLETED
        request.completed_at = datetime.now()
        
        return True
        
    async def clone_environment(self, source_env_id: str,
                               new_name: str,
                               include_data: bool = False) -> Optional[Environment]:
        """Клонирование окружения"""
        source = self.environments.get(source_env_id)
        if not source:
            return None
            
        clone_record = EnvironmentClone(
            clone_id=f"clone_{uuid.uuid4().hex[:8]}",
            source_env_id=source_env_id,
            include_data=include_data
        )
        
        # Create cloned environment
        new_env = await self.create_environment(
            new_name,
            source.env_type,
            source.resource_tier,
            source.config.config_id if source.config else "",
            source.owner,
            source.team
        )
        
        clone_record.target_env_id = new_env.env_id
        clone_record.status = "completed"
        clone_record.progress_percent = 100
        clone_record.completed_at = datetime.now()
        
        self.clones[clone_record.clone_id] = clone_record
        
        # Copy deployed version
        if source.deployed_version:
            await self.deploy_to_environment(new_env.env_id, source.deployed_version)
            
        return new_env
        
    async def stop_environment(self, env_id: str) -> bool:
        """Остановка окружения"""
        env = self.environments.get(env_id)
        if not env:
            return False
            
        await asyncio.sleep(0.05)
        env.status = EnvironmentStatus.STOPPED
        env.updated_at = datetime.now()
        
        return True
        
    async def terminate_environment(self, env_id: str) -> bool:
        """Терминация окружения"""
        env = self.environments.get(env_id)
        if not env:
            return False
            
        env.status = EnvironmentStatus.TERMINATING
        await asyncio.sleep(0.05)
        env.status = EnvironmentStatus.TERMINATED
        env.updated_at = datetime.now()
        
        return True
        
    def generate_cost_report(self, env_id: str, days: int = 30) -> CostReport:
        """Генерация отчёта о затратах"""
        env = self.environments.get(env_id)
        if not env:
            return CostReport(report_id=f"cost_{uuid.uuid4().hex[:8]}")
            
        hours = days * 24
        
        # Calculate based on resource spec
        compute_cost = (env.resource_spec.cpu_cores * 0.05 +
                       env.resource_spec.memory_gb * 0.01) * hours * env.resource_spec.replicas
        storage_cost = env.resource_spec.storage_gb * 0.001 * hours
        network_cost = random.uniform(5, 20)
        database_cost = env.resource_spec.database_size_gb * 0.002 * hours
        
        report = CostReport(
            report_id=f"cost_{uuid.uuid4().hex[:8]}",
            env_id=env_id,
            period_start=datetime.now() - timedelta(days=days),
            period_end=datetime.now(),
            compute_cost=compute_cost,
            storage_cost=storage_cost,
            network_cost=network_cost,
            database_cost=database_cost,
            total_cost=compute_cost + storage_cost + network_cost + database_cost
        )
        
        self.cost_reports.append(report)
        return report
        
    def cleanup_expired(self) -> List[str]:
        """Очистка истёкших окружений"""
        expired = []
        now = datetime.now()
        
        for env in self.environments.values():
            if env.expires_at and env.expires_at < now:
                if env.status == EnvironmentStatus.RUNNING:
                    expired.append(env.env_id)
                    
        return expired
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        running = [e for e in self.environments.values() if e.status == EnvironmentStatus.RUNNING]
        total_monthly = sum(e.monthly_cost for e in running)
        
        by_type = {}
        for env in self.environments.values():
            t = env.env_type.value
            if t not in by_type:
                by_type[t] = 0
            by_type[t] += 1
            
        return {
            "total_environments": len(self.environments),
            "running_environments": len(running),
            "stopped_environments": len([e for e in self.environments.values() if e.status == EnvironmentStatus.STOPPED]),
            "terminated_environments": len([e for e in self.environments.values() if e.status == EnvironmentStatus.TERMINATED]),
            "environments_by_type": by_type,
            "total_configs": len(self.configs),
            "pending_promotions": len([p for p in self.promotions.values() if p.status == PromotionStatus.PENDING]),
            "completed_promotions": len([p for p in self.promotions.values() if p.status == PromotionStatus.COMPLETED]),
            "total_clones": len(self.clones),
            "total_monthly_cost": total_monthly
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 218: Environment Manager Platform")
    print("=" * 60)
    
    platform = EnvironmentManagerPlatform()
    print("✓ Environment Manager Platform created")
    
    # Create configurations
    print("\n⚙️ Creating Configurations...")
    
    dev_config = platform.create_config(
        "Development Config",
        {"debug": True, "log_level": "DEBUG", "db_pool_size": 5},
        {"new_ui": True, "beta_features": True}
    )
    print(f"  ✓ {dev_config.name}")
    
    staging_config = platform.create_config(
        "Staging Config",
        {"debug": False, "log_level": "INFO", "db_pool_size": 10},
        {"new_ui": True, "beta_features": False}
    )
    print(f"  ✓ {staging_config.name}")
    
    prod_config = platform.create_config(
        "Production Config",
        {"debug": False, "log_level": "WARNING", "db_pool_size": 50},
        {"new_ui": False, "beta_features": False}
    )
    print(f"  ✓ {prod_config.name}")
    
    # Create environments
    print("\n🌍 Creating Environments...")
    
    envs = []
    
    # Development
    dev_env = await platform.create_environment(
        "api-dev",
        EnvironmentType.DEVELOPMENT,
        ResourceTier.MINIMAL,
        dev_config.config_id,
        "dev-team",
        "backend"
    )
    envs.append(dev_env)
    print(f"  ✓ {dev_env.name}: {dev_env.url}")
    
    # Staging
    staging_env = await platform.create_environment(
        "api-staging",
        EnvironmentType.STAGING,
        ResourceTier.STANDARD,
        staging_config.config_id,
        "dev-team",
        "backend"
    )
    envs.append(staging_env)
    print(f"  ✓ {staging_env.name}: {staging_env.url}")
    
    # Production
    prod_env = await platform.create_environment(
        "api-prod",
        EnvironmentType.PRODUCTION,
        ResourceTier.PRODUCTION,
        prod_config.config_id,
        "platform-team",
        "backend"
    )
    envs.append(prod_env)
    print(f"  ✓ {prod_env.name}: {prod_env.url}")
    
    # Preview environment
    preview_env = await platform.create_environment(
        "api-preview-pr123",
        EnvironmentType.PREVIEW,
        ResourceTier.MINIMAL,
        dev_config.config_id,
        "dev",
        "backend"
    )
    envs.append(preview_env)
    print(f"  ✓ {preview_env.name}: TTL {preview_env.ttl_hours}h")
    
    # Deploy versions
    print("\n🚀 Deploying Versions...")
    
    await platform.deploy_to_environment(dev_env.env_id, "v2.3.0-dev")
    print(f"  ✓ {dev_env.name}: v2.3.0-dev")
    
    await platform.deploy_to_environment(staging_env.env_id, "v2.2.0")
    print(f"  ✓ {staging_env.name}: v2.2.0")
    
    await platform.deploy_to_environment(prod_env.env_id, "v2.1.5")
    print(f"  ✓ {prod_env.name}: v2.1.5")
    
    # Request promotion
    print("\n📤 Requesting Promotion...")
    
    promo = await platform.request_promotion(
        staging_env.env_id,
        EnvironmentType.PRODUCTION,
        "developer@example.com",
        "Release v2.2.0 - new features"
    )
    print(f"  ✓ Promotion request: {staging_env.deployed_version} -> {promo.target_env_type.value}")
    
    # Approve promotion
    await platform.approve_promotion(promo.request_id, "lead@example.com")
    print(f"  ✓ Promotion approved and completed")
    
    # Clone environment
    print("\n📋 Cloning Environment...")
    
    clone = await platform.clone_environment(
        dev_env.env_id,
        "api-dev-feature-x"
    )
    if clone:
        envs.append(clone)
        print(f"  ✓ Cloned {dev_env.name} -> {clone.name}")
        
    # Display environments
    print("\n🌍 Environment Inventory:")
    
    print("\n  ┌────────────────────┬─────────────┬──────────┬────────────┬────────────┐")
    print("  │ Environment        │ Type        │ Tier     │ Version    │ Cost/mo    │")
    print("  ├────────────────────┼─────────────┼──────────┼────────────┼────────────┤")
    
    for env in platform.environments.values():
        name = env.name[:18].ljust(18)
        etype = env.env_type.value[:11].ljust(11)
        tier = env.resource_tier.value[:8].ljust(8)
        version = (env.deployed_version or "N/A")[:10].ljust(10)
        cost = f"${env.monthly_cost:.2f}"[:10].ljust(10)
        
        print(f"  │ {name} │ {etype} │ {tier} │ {version} │ {cost} │")
        
    print("  └────────────────────┴─────────────┴──────────┴────────────┴────────────┘")
    
    # Environment details
    print("\n📊 Environment Details:")
    
    for env in list(platform.environments.values())[:3]:
        status_icons = {
            EnvironmentStatus.RUNNING: "🟢",
            EnvironmentStatus.STOPPED: "🟡",
            EnvironmentStatus.TERMINATED: "🔴"
        }
        icon = status_icons.get(env.status, "⚪")
        
        print(f"\n  {icon} {env.name}:")
        print(f"      URL: {env.url}")
        print(f"      Status: {env.status.value}")
        print(f"      Resources: {env.resource_spec.cpu_cores}CPU, {env.resource_spec.memory_gb}GB RAM")
        print(f"      Replicas: {env.resource_spec.replicas}")
        if env.expires_at:
            print(f"      Expires: {env.expires_at.strftime('%Y-%m-%d %H:%M')}")
            
    # Resource allocation
    print("\n💻 Resource Allocation:")
    
    total_cpu = sum(e.resource_spec.cpu_cores * e.resource_spec.replicas
                   for e in platform.environments.values()
                   if e.status == EnvironmentStatus.RUNNING)
    total_memory = sum(e.resource_spec.memory_gb * e.resource_spec.replicas
                      for e in platform.environments.values()
                      if e.status == EnvironmentStatus.RUNNING)
    total_storage = sum(e.resource_spec.storage_gb
                       for e in platform.environments.values()
                       if e.status == EnvironmentStatus.RUNNING)
    
    print(f"  Total CPU: {total_cpu} cores")
    cpu_bar = "█" * min(20, total_cpu) + "░" * max(0, 20 - total_cpu)
    print(f"  [{cpu_bar}]")
    
    print(f"\n  Total Memory: {total_memory}GB")
    mem_bar = "█" * min(20, total_memory // 5) + "░" * max(0, 20 - total_memory // 5)
    print(f"  [{mem_bar}]")
    
    print(f"\n  Total Storage: {total_storage}GB")
    storage_bar = "█" * min(20, total_storage // 50) + "░" * max(0, 20 - total_storage // 50)
    print(f"  [{storage_bar}]")
    
    # Cost analysis
    print("\n💰 Cost Analysis:")
    
    for env in list(platform.environments.values())[:4]:
        if env.status != EnvironmentStatus.RUNNING:
            continue
        report = platform.generate_cost_report(env.env_id)
        
        print(f"\n  {env.name}:")
        print(f"    Compute: ${report.compute_cost:.2f}")
        print(f"    Storage: ${report.storage_cost:.2f}")
        print(f"    Network: ${report.network_cost:.2f}")
        print(f"    Total: ${report.total_cost:.2f}")
        
    # Cost by type
    print("\n💵 Monthly Cost by Environment Type:")
    
    cost_by_type = {}
    for env in platform.environments.values():
        if env.status != EnvironmentStatus.RUNNING:
            continue
        t = env.env_type.value
        if t not in cost_by_type:
            cost_by_type[t] = 0
        cost_by_type[t] += env.monthly_cost
        
    for etype, cost in sorted(cost_by_type.items(), key=lambda x: -x[1]):
        bar_len = int(cost / 50)
        bar = "█" * min(20, bar_len) + "░" * max(0, 20 - bar_len)
        print(f"  {etype:12s} [{bar}] ${cost:.2f}")
        
    # Promotions
    print("\n📤 Promotion History:")
    
    for promo in platform.promotions.values():
        source = platform.environments.get(promo.source_env_id)
        source_name = source.name if source else "unknown"
        
        status_icons = {
            PromotionStatus.COMPLETED: "✅",
            PromotionStatus.PENDING: "⏳",
            PromotionStatus.FAILED: "❌"
        }
        icon = status_icons.get(promo.status, "⚪")
        
        print(f"  {icon} {source_name} -> {promo.target_env_type.value}")
        print(f"      Version: {promo.version}")
        print(f"      Status: {promo.status.value}")
        if promo.approver:
            print(f"      Approved by: {promo.approver}")
            
    # Configuration comparison
    print("\n⚙️ Configuration Comparison:")
    
    configs_list = list(platform.configs.values())
    if len(configs_list) >= 2:
        print(f"\n  {'Setting':<20} {'Dev':<15} {'Staging':<15} {'Prod':<15}")
        print(f"  {'-'*20} {'-'*15} {'-'*15} {'-'*15}")
        
        all_keys = set()
        for c in configs_list:
            all_keys.update(c.values.keys())
            
        for key in sorted(all_keys):
            values = []
            for c in configs_list[:3]:
                v = str(c.values.get(key, "N/A"))[:14]
                values.append(v.ljust(15))
            print(f"  {key:<20} {''.join(values)}")
            
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Environments: {stats['total_environments']}")
    print(f"  Running: {stats['running_environments']}")
    print(f"  Stopped: {stats['stopped_environments']}")
    print(f"  Configs: {stats['total_configs']}")
    print(f"  Promotions: {stats['completed_promotions']}")
    print(f"  Clones: {stats['total_clones']}")
    print(f"  Monthly Cost: ${stats['total_monthly_cost']:.2f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Environment Manager Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Environments:            {stats['total_environments']:>12}                        │")
    print(f"│ Running:                       {stats['running_environments']:>12}                        │")
    print(f"│ Configurations:                {stats['total_configs']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Monthly Cost:                       ${stats['total_monthly_cost']:>10.2f}               │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Environment Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
