#!/usr/bin/env python3
"""
Server Init - Iteration 366: CMDB Platform
Платформа Configuration Management Database

Функционал:
- Configuration Items (CI) - элементы конфигурации
- Relationships - связи между CI
- Change Tracking - отслеживание изменений
- Discovery Integration - интеграция с обнаружением
- Impact Analysis - анализ влияния
- Compliance Management - управление соответствием
- Audit Trail - журнал аудита
- Visualization - визуализация
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import uuid


class CIType(Enum):
    """Тип элемента конфигурации"""
    SERVER = "server"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER = "container"
    DATABASE = "database"
    APPLICATION = "application"
    SERVICE = "service"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    LOAD_BALANCER = "load_balancer"
    CLUSTER = "cluster"


class CIStatus(Enum):
    """Статус CI"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"
    PENDING = "pending"


class RelationshipType(Enum):
    """Тип связи"""
    RUNS_ON = "runs_on"
    DEPENDS_ON = "depends_on"
    CONNECTS_TO = "connects_to"
    CONTAINS = "contains"
    MANAGED_BY = "managed_by"
    HOSTED_ON = "hosted_on"
    USES = "uses"
    PART_OF = "part_of"


class ChangeType(Enum):
    """Тип изменения"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELATIONSHIP_ADD = "relationship_add"
    RELATIONSHIP_REMOVE = "relationship_remove"


class DiscoverySource(Enum):
    """Источник обнаружения"""
    MANUAL = "manual"
    CLOUD_API = "cloud_api"
    AGENT = "agent"
    SCANNER = "scanner"
    INTEGRATION = "integration"


class ComplianceStatus(Enum):
    """Статус соответствия"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"
    EXEMPT = "exempt"


@dataclass
class Attribute:
    """Атрибут CI"""
    attr_id: str
    name: str
    value: Any
    data_type: str = "string"  # string, number, boolean, date, json
    is_required: bool = False
    is_indexed: bool = False
    source: DiscoverySource = DiscoverySource.MANUAL
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """Связь между CI"""
    relationship_id: str
    
    # CIs
    source_ci_id: str = ""
    target_ci_id: str = ""
    
    # Type
    relationship_type: RelationshipType = RelationshipType.DEPENDS_ON
    
    # Direction
    is_bidirectional: bool = False
    
    # Metadata
    description: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ConfigurationItem:
    """Элемент конфигурации"""
    ci_id: str
    
    # Identity
    name: str = ""
    display_name: str = ""
    description: str = ""
    
    # Type
    ci_type: CIType = CIType.SERVER
    ci_class: str = ""  # subtype
    
    # Status
    status: CIStatus = CIStatus.ACTIVE
    
    # Location
    location: str = ""
    environment: str = ""  # production, staging, development
    
    # Owner
    owner_id: str = ""
    owner_team: str = ""
    
    # Attributes
    attributes: Dict[str, Attribute] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Discovery
    discovery_source: DiscoverySource = DiscoverySource.MANUAL
    last_discovered: Optional[datetime] = None
    
    # Compliance
    compliance_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    compliance_policies: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class ChangeRecord:
    """Запись изменения"""
    change_id: str
    
    # Target
    ci_id: str = ""
    
    # Change type
    change_type: ChangeType = ChangeType.UPDATE
    
    # Changes
    field_name: str = ""
    old_value: Any = None
    new_value: Any = None
    
    # Actor
    changed_by: str = ""
    
    # Source
    source: str = ""  # manual, discovery, api
    
    # Related change request
    change_request_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CIClass:
    """Класс CI"""
    class_id: str
    
    # Identity
    name: str = ""
    display_name: str = ""
    description: str = ""
    
    # Parent class
    parent_class: str = ""
    
    # CI Type
    ci_type: CIType = CIType.SERVER
    
    # Attributes schema
    attribute_schema: List[Dict[str, Any]] = field(default_factory=list)
    
    # Allowed relationships
    allowed_relationships: List[RelationshipType] = field(default_factory=list)


@dataclass
class CompliancePolicy:
    """Политика соответствия"""
    policy_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    
    # Scope
    ci_types: List[CIType] = field(default_factory=list)
    environments: List[str] = field(default_factory=list)
    
    # Rules
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Severity
    severity: str = "medium"  # low, medium, high, critical
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComplianceViolation:
    """Нарушение соответствия"""
    violation_id: str
    
    # References
    ci_id: str = ""
    policy_id: str = ""
    
    # Details
    rule_name: str = ""
    message: str = ""
    
    # Severity
    severity: str = "medium"
    
    # Status
    status: str = "open"  # open, acknowledged, resolved, suppressed
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class DiscoveryJob:
    """Задание обнаружения"""
    job_id: str
    
    # Identity
    name: str = ""
    
    # Source
    source: DiscoverySource = DiscoverySource.SCANNER
    
    # Scope
    targets: List[str] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    
    # Results
    discovered_cis: int = 0
    updated_cis: int = 0
    errors: List[str] = field(default_factory=list)
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ImpactReport:
    """Отчет о влиянии"""
    report_id: str
    
    # Source CI
    source_ci_id: str = ""
    
    # Impact type
    impact_type: str = ""  # change, failure, maintenance
    
    # Affected CIs
    directly_affected: List[str] = field(default_factory=list)
    indirectly_affected: List[str] = field(default_factory=list)
    
    # Summary
    total_affected: int = 0
    critical_services_affected: int = 0
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CMDBMetrics:
    """Метрики CMDB"""
    metrics_id: str
    
    # Counts
    total_cis: int = 0
    active_cis: int = 0
    
    # By type
    cis_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Relationships
    total_relationships: int = 0
    
    # Compliance
    compliant_cis: int = 0
    non_compliant_cis: int = 0
    compliance_rate: float = 0.0
    
    # Discovery
    last_discovery_run: Optional[datetime] = None
    
    # Changes
    changes_last_24h: int = 0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class CMDBPlatform:
    """Платформа CMDB"""
    
    def __init__(self, platform_name: str = "cmdb"):
        self.platform_name = platform_name
        self.cis: Dict[str, ConfigurationItem] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.ci_classes: Dict[str, CIClass] = {}
        self.change_history: List[ChangeRecord] = []
        self.policies: Dict[str, CompliancePolicy] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.discovery_jobs: Dict[str, DiscoveryJob] = {}
        
        # Initialize default classes
        self._init_default_classes()
        
    def _init_default_classes(self):
        """Инициализация классов CI по умолчанию"""
        default_classes = [
            ("server", "Physical Server", CIType.SERVER, [
                {"name": "cpu_cores", "type": "number", "required": True},
                {"name": "memory_gb", "type": "number", "required": True},
                {"name": "os", "type": "string", "required": True}
            ]),
            ("vm", "Virtual Machine", CIType.VIRTUAL_MACHINE, [
                {"name": "cpu_cores", "type": "number", "required": True},
                {"name": "memory_gb", "type": "number", "required": True},
                {"name": "hypervisor", "type": "string", "required": False}
            ]),
            ("container", "Container", CIType.CONTAINER, [
                {"name": "image", "type": "string", "required": True},
                {"name": "ports", "type": "json", "required": False}
            ]),
            ("database", "Database Instance", CIType.DATABASE, [
                {"name": "engine", "type": "string", "required": True},
                {"name": "version", "type": "string", "required": True},
                {"name": "storage_gb", "type": "number", "required": False}
            ]),
            ("application", "Application", CIType.APPLICATION, [
                {"name": "version", "type": "string", "required": True},
                {"name": "language", "type": "string", "required": False}
            ]),
            ("service", "Business Service", CIType.SERVICE, [
                {"name": "tier", "type": "number", "required": True},
                {"name": "sla", "type": "number", "required": False}
            ])
        ]
        
        for name, display, ci_type, attrs in default_classes:
            ci_class = CIClass(
                class_id=f"cls_{uuid.uuid4().hex[:8]}",
                name=name,
                display_name=display,
                ci_type=ci_type,
                attribute_schema=attrs,
                allowed_relationships=list(RelationshipType)
            )
            self.ci_classes[ci_class.class_id] = ci_class
            
    async def create_ci(self, name: str,
                       ci_type: CIType,
                       ci_class: str = "",
                       description: str = "",
                       environment: str = "production",
                       location: str = "",
                       owner_team: str = "",
                       attributes: Dict[str, Any] = None,
                       tags: List[str] = None,
                       source: DiscoverySource = DiscoverySource.MANUAL) -> ConfigurationItem:
        """Создание CI"""
        ci = ConfigurationItem(
            ci_id=f"ci_{uuid.uuid4().hex[:8]}",
            name=name,
            display_name=name,
            description=description,
            ci_type=ci_type,
            ci_class=ci_class,
            environment=environment,
            location=location,
            owner_team=owner_team,
            tags=tags or [],
            discovery_source=source,
            last_discovered=datetime.now() if source != DiscoverySource.MANUAL else None
        )
        
        # Add attributes
        if attributes:
            for attr_name, attr_value in attributes.items():
                ci.attributes[attr_name] = Attribute(
                    attr_id=f"attr_{uuid.uuid4().hex[:8]}",
                    name=attr_name,
                    value=attr_value,
                    source=source
                )
                
        self.cis[ci.ci_id] = ci
        
        # Record change
        await self._record_change(ci.ci_id, ChangeType.CREATE, "ci", None, ci.name, "system")
        
        return ci
        
    async def update_ci(self, ci_id: str,
                       updates: Dict[str, Any],
                       changed_by: str = "") -> Optional[ConfigurationItem]:
        """Обновление CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return None
            
        for field_name, new_value in updates.items():
            old_value = getattr(ci, field_name, None)
            if hasattr(ci, field_name):
                setattr(ci, field_name, new_value)
                await self._record_change(ci_id, ChangeType.UPDATE, field_name, old_value, new_value, changed_by)
                
        ci.updated_at = datetime.now()
        return ci
        
    async def update_attribute(self, ci_id: str,
                              attr_name: str,
                              attr_value: Any,
                              changed_by: str = "") -> Optional[ConfigurationItem]:
        """Обновление атрибута CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return None
            
        old_value = ci.attributes.get(attr_name)
        old_val = old_value.value if old_value else None
        
        ci.attributes[attr_name] = Attribute(
            attr_id=f"attr_{uuid.uuid4().hex[:8]}",
            name=attr_name,
            value=attr_value
        )
        
        ci.updated_at = datetime.now()
        
        await self._record_change(ci_id, ChangeType.UPDATE, f"attr:{attr_name}", old_val, attr_value, changed_by)
        
        return ci
        
    async def delete_ci(self, ci_id: str, deleted_by: str = "") -> bool:
        """Удаление CI"""
        if ci_id not in self.cis:
            return False
            
        ci = self.cis[ci_id]
        
        # Remove relationships
        to_remove = [r_id for r_id, r in self.relationships.items()
                     if r.source_ci_id == ci_id or r.target_ci_id == ci_id]
        for r_id in to_remove:
            del self.relationships[r_id]
            
        # Record change
        await self._record_change(ci_id, ChangeType.DELETE, "ci", ci.name, None, deleted_by)
        
        del self.cis[ci_id]
        return True
        
    async def create_relationship(self, source_ci_id: str,
                                 target_ci_id: str,
                                 relationship_type: RelationshipType,
                                 description: str = "",
                                 is_bidirectional: bool = False) -> Optional[Relationship]:
        """Создание связи"""
        if source_ci_id not in self.cis or target_ci_id not in self.cis:
            return None
            
        relationship = Relationship(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_ci_id=source_ci_id,
            target_ci_id=target_ci_id,
            relationship_type=relationship_type,
            description=description,
            is_bidirectional=is_bidirectional
        )
        
        self.relationships[relationship.relationship_id] = relationship
        
        # Record change
        await self._record_change(
            source_ci_id,
            ChangeType.RELATIONSHIP_ADD,
            f"relationship:{target_ci_id}",
            None,
            relationship_type.value,
            "system"
        )
        
        return relationship
        
    async def delete_relationship(self, relationship_id: str) -> bool:
        """Удаление связи"""
        if relationship_id not in self.relationships:
            return False
            
        rel = self.relationships[relationship_id]
        
        await self._record_change(
            rel.source_ci_id,
            ChangeType.RELATIONSHIP_REMOVE,
            f"relationship:{rel.target_ci_id}",
            rel.relationship_type.value,
            None,
            "system"
        )
        
        del self.relationships[relationship_id]
        return True
        
    async def _record_change(self, ci_id: str,
                            change_type: ChangeType,
                            field_name: str,
                            old_value: Any,
                            new_value: Any,
                            changed_by: str):
        """Запись изменения"""
        change = ChangeRecord(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            ci_id=ci_id,
            change_type=change_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by
        )
        
        self.change_history.append(change)
        
    async def get_relationships(self, ci_id: str,
                               relationship_type: RelationshipType = None,
                               direction: str = "both") -> List[Relationship]:
        """Получение связей CI"""
        results = []
        
        for rel in self.relationships.values():
            if direction in ["outgoing", "both"] and rel.source_ci_id == ci_id:
                if relationship_type is None or rel.relationship_type == relationship_type:
                    results.append(rel)
                    
            if direction in ["incoming", "both"] and rel.target_ci_id == ci_id:
                if relationship_type is None or rel.relationship_type == relationship_type:
                    results.append(rel)
                    
            if rel.is_bidirectional and direction == "both":
                if rel.target_ci_id == ci_id or rel.source_ci_id == ci_id:
                    if rel not in results:
                        if relationship_type is None or rel.relationship_type == relationship_type:
                            results.append(rel)
                            
        return results
        
    async def analyze_impact(self, ci_id: str,
                            impact_type: str = "failure",
                            depth: int = 3) -> ImpactReport:
        """Анализ влияния"""
        directly_affected: Set[str] = set()
        indirectly_affected: Set[str] = set()
        
        # Find directly dependent CIs
        for rel in self.relationships.values():
            if rel.target_ci_id == ci_id and rel.relationship_type == RelationshipType.DEPENDS_ON:
                directly_affected.add(rel.source_ci_id)
                
        # Find indirectly affected (cascade)
        current_level = directly_affected.copy()
        for _ in range(depth - 1):
            next_level: Set[str] = set()
            for affected_ci in current_level:
                for rel in self.relationships.values():
                    if rel.target_ci_id == affected_ci and rel.relationship_type == RelationshipType.DEPENDS_ON:
                        if rel.source_ci_id not in directly_affected:
                            next_level.add(rel.source_ci_id)
            indirectly_affected.update(next_level)
            current_level = next_level
            
        # Count critical services
        critical_count = 0
        for ci_id in directly_affected | indirectly_affected:
            ci = self.cis.get(ci_id)
            if ci and ci.ci_type == CIType.SERVICE:
                tier = ci.attributes.get("tier")
                if tier and tier.value == 1:
                    critical_count += 1
                    
        return ImpactReport(
            report_id=f"imp_{uuid.uuid4().hex[:8]}",
            source_ci_id=ci_id,
            impact_type=impact_type,
            directly_affected=list(directly_affected),
            indirectly_affected=list(indirectly_affected),
            total_affected=len(directly_affected) + len(indirectly_affected),
            critical_services_affected=critical_count
        )
        
    async def create_policy(self, name: str,
                           description: str = "",
                           ci_types: List[CIType] = None,
                           environments: List[str] = None,
                           rules: List[Dict[str, Any]] = None,
                           severity: str = "medium") -> CompliancePolicy:
        """Создание политики соответствия"""
        policy = CompliancePolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            ci_types=ci_types or [],
            environments=environments or [],
            rules=rules or [],
            severity=severity
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def check_compliance(self, ci_id: str) -> List[ComplianceViolation]:
        """Проверка соответствия CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return []
            
        violations = []
        
        for policy in self.policies.values():
            if not policy.is_enabled:
                continue
                
            # Check if policy applies
            if policy.ci_types and ci.ci_type not in policy.ci_types:
                continue
            if policy.environments and ci.environment not in policy.environments:
                continue
                
            # Check rules
            for rule in policy.rules:
                rule_name = rule.get("name", "")
                attr_name = rule.get("attribute", "")
                condition = rule.get("condition", "exists")
                expected = rule.get("value")
                
                attr = ci.attributes.get(attr_name)
                attr_value = attr.value if attr else None
                
                violation = None
                
                if condition == "exists" and attr_value is None:
                    violation = f"Required attribute '{attr_name}' is missing"
                elif condition == "equals" and attr_value != expected:
                    violation = f"Attribute '{attr_name}' should be '{expected}', got '{attr_value}'"
                elif condition == "min" and attr_value is not None and attr_value < expected:
                    violation = f"Attribute '{attr_name}' should be >= {expected}, got {attr_value}"
                elif condition == "max" and attr_value is not None and attr_value > expected:
                    violation = f"Attribute '{attr_name}' should be <= {expected}, got {attr_value}"
                    
                if violation:
                    v = ComplianceViolation(
                        violation_id=f"vio_{uuid.uuid4().hex[:8]}",
                        ci_id=ci_id,
                        policy_id=policy.policy_id,
                        rule_name=rule_name,
                        message=violation,
                        severity=policy.severity
                    )
                    violations.append(v)
                    self.violations[v.violation_id] = v
                    
        # Update CI compliance status
        if violations:
            ci.compliance_status = ComplianceStatus.NON_COMPLIANT
        else:
            ci.compliance_status = ComplianceStatus.COMPLIANT
            
        return violations
        
    async def run_discovery(self, name: str,
                           source: DiscoverySource,
                           targets: List[str] = None) -> DiscoveryJob:
        """Запуск обнаружения"""
        job = DiscoveryJob(
            job_id=f"dsc_{uuid.uuid4().hex[:8]}",
            name=name,
            source=source,
            targets=targets or [],
            status="running",
            started_at=datetime.now()
        )
        
        self.discovery_jobs[job.job_id] = job
        
        # Simulate discovery
        await asyncio.sleep(0.1)
        
        # Simulate discovered CIs
        job.discovered_cis = random.randint(5, 20)
        job.updated_cis = random.randint(0, job.discovered_cis // 2)
        job.status = "completed"
        job.completed_at = datetime.now()
        
        return job
        
    async def collect_metrics(self) -> CMDBMetrics:
        """Сбор метрик"""
        active_cis = sum(1 for ci in self.cis.values() if ci.status == CIStatus.ACTIVE)
        
        cis_by_type = {}
        for ci_type in CIType:
            cis_by_type[ci_type.value] = sum(1 for ci in self.cis.values() if ci.ci_type == ci_type)
            
        compliant = sum(1 for ci in self.cis.values() if ci.compliance_status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for ci in self.cis.values() if ci.compliance_status == ComplianceStatus.NON_COMPLIANT)
        
        compliance_rate = (compliant / len(self.cis) * 100) if self.cis else 0.0
        
        # Changes in last 24 hours
        now = datetime.now()
        changes_24h = sum(
            1 for c in self.change_history
            if (now - c.timestamp).total_seconds() < 86400
        )
        
        # Last discovery
        last_discovery = None
        for job in self.discovery_jobs.values():
            if job.completed_at:
                if last_discovery is None or job.completed_at > last_discovery:
                    last_discovery = job.completed_at
                    
        return CMDBMetrics(
            metrics_id=f"cmm_{uuid.uuid4().hex[:8]}",
            total_cis=len(self.cis),
            active_cis=active_cis,
            cis_by_type=cis_by_type,
            total_relationships=len(self.relationships),
            compliant_cis=compliant,
            non_compliant_cis=non_compliant,
            compliance_rate=compliance_rate,
            last_discovery_run=last_discovery,
            changes_last_24h=changes_24h
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        by_status = {}
        for status in CIStatus:
            by_status[status.value] = sum(1 for ci in self.cis.values() if ci.status == status)
            
        by_type = {}
        for ci_type in CIType:
            by_type[ci_type.value] = sum(1 for ci in self.cis.values() if ci.ci_type == ci_type)
            
        by_environment = {}
        for ci in self.cis.values():
            env = ci.environment or "unknown"
            by_environment[env] = by_environment.get(env, 0) + 1
            
        rel_by_type = {}
        for rel_type in RelationshipType:
            rel_by_type[rel_type.value] = sum(1 for r in self.relationships.values() if r.relationship_type == rel_type)
            
        open_violations = sum(1 for v in self.violations.values() if v.status == "open")
        
        return {
            "total_cis": len(self.cis),
            "by_status": by_status,
            "by_type": by_type,
            "by_environment": by_environment,
            "total_relationships": len(self.relationships),
            "relationships_by_type": rel_by_type,
            "ci_classes": len(self.ci_classes),
            "change_history_count": len(self.change_history),
            "policies": len(self.policies),
            "open_violations": open_violations,
            "discovery_jobs": len(self.discovery_jobs)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 366: CMDB Platform")
    print("=" * 60)
    
    platform = CMDBPlatform(platform_name="enterprise-cmdb")
    print("✓ CMDB Platform initialized")
    print(f"  📦 {len(platform.ci_classes)} CI classes loaded")
    
    # Create CIs - Infrastructure Layer
    print("\n🖥️ Creating Infrastructure CIs...")
    
    servers_data = [
        ("srv-prod-01", "production", "us-east-1", {"cpu_cores": 32, "memory_gb": 128, "os": "Ubuntu 22.04"}),
        ("srv-prod-02", "production", "us-east-1", {"cpu_cores": 32, "memory_gb": 128, "os": "Ubuntu 22.04"}),
        ("srv-prod-03", "production", "us-west-2", {"cpu_cores": 16, "memory_gb": 64, "os": "Ubuntu 22.04"}),
        ("srv-staging-01", "staging", "us-east-1", {"cpu_cores": 8, "memory_gb": 32, "os": "Ubuntu 22.04"})
    ]
    
    servers = []
    for name, env, location, attrs in servers_data:
        ci = await platform.create_ci(name, CIType.SERVER, "server", f"Physical server {name}", env, location, "Infrastructure Team", attrs, ["infrastructure"])
        servers.append(ci)
        print(f"  🖥️ {name} ({env})")
        
    # Create VMs
    print("\n💻 Creating Virtual Machines...")
    
    vms_data = [
        ("vm-api-01", "production", {"cpu_cores": 4, "memory_gb": 16, "hypervisor": "KVM"}),
        ("vm-api-02", "production", {"cpu_cores": 4, "memory_gb": 16, "hypervisor": "KVM"}),
        ("vm-worker-01", "production", {"cpu_cores": 8, "memory_gb": 32, "hypervisor": "KVM"}),
        ("vm-db-01", "production", {"cpu_cores": 8, "memory_gb": 64, "hypervisor": "KVM"})
    ]
    
    vms = []
    for name, env, attrs in vms_data:
        ci = await platform.create_ci(name, CIType.VIRTUAL_MACHINE, "vm", f"Virtual machine {name}", env, "us-east-1", "Platform Team", attrs, ["compute"])
        vms.append(ci)
        print(f"  💻 {name}")
        
    # Create Databases
    print("\n🗄️ Creating Databases...")
    
    dbs_data = [
        ("db-primary", "production", {"engine": "PostgreSQL", "version": "15.2", "storage_gb": 500}),
        ("db-replica", "production", {"engine": "PostgreSQL", "version": "15.2", "storage_gb": 500}),
        ("cache-redis", "production", {"engine": "Redis", "version": "7.0", "storage_gb": 32})
    ]
    
    databases = []
    for name, env, attrs in dbs_data:
        ci = await platform.create_ci(name, CIType.DATABASE, "database", f"Database {name}", env, "us-east-1", "DBA Team", attrs, ["data"])
        databases.append(ci)
        print(f"  🗄️ {name} ({attrs['engine']})")
        
    # Create Applications
    print("\n📱 Creating Applications...")
    
    apps_data = [
        ("api-gateway", "production", {"version": "2.5.0", "language": "Go"}),
        ("payment-service", "production", {"version": "1.8.0", "language": "Java"}),
        ("user-service", "production", {"version": "3.2.1", "language": "Python"}),
        ("notification-service", "production", {"version": "1.5.0", "language": "Node.js"})
    ]
    
    applications = []
    for name, env, attrs in apps_data:
        ci = await platform.create_ci(name, CIType.APPLICATION, "application", f"Application {name}", env, "us-east-1", "Development Team", attrs, ["application"])
        applications.append(ci)
        print(f"  📱 {name} v{attrs['version']}")
        
    # Create Services
    print("\n🔧 Creating Business Services...")
    
    services_data = [
        ("Payment Processing", "production", {"tier": 1, "sla": 99.99}),
        ("User Management", "production", {"tier": 2, "sla": 99.9}),
        ("Notifications", "production", {"tier": 3, "sla": 99.5})
    ]
    
    services = []
    for name, env, attrs in services_data:
        ci = await platform.create_ci(name, CIType.SERVICE, "service", f"Business service: {name}", env, "", "Business Team", attrs, ["service"])
        services.append(ci)
        print(f"  🔧 {name} (Tier {attrs['tier']})")
        
    # Create Relationships
    print("\n🔗 Creating Relationships...")
    
    # VMs run on servers
    await platform.create_relationship(vms[0].ci_id, servers[0].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(vms[1].ci_id, servers[0].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(vms[2].ci_id, servers[1].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(vms[3].ci_id, servers[1].ci_id, RelationshipType.RUNS_ON)
    
    # Applications run on VMs
    await platform.create_relationship(applications[0].ci_id, vms[0].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(applications[1].ci_id, vms[1].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(applications[2].ci_id, vms[0].ci_id, RelationshipType.RUNS_ON)
    await platform.create_relationship(applications[3].ci_id, vms[2].ci_id, RelationshipType.RUNS_ON)
    
    # Applications depend on databases
    await platform.create_relationship(applications[0].ci_id, databases[2].ci_id, RelationshipType.DEPENDS_ON)
    await platform.create_relationship(applications[1].ci_id, databases[0].ci_id, RelationshipType.DEPENDS_ON)
    await platform.create_relationship(applications[2].ci_id, databases[0].ci_id, RelationshipType.DEPENDS_ON)
    
    # Services depend on applications
    await platform.create_relationship(services[0].ci_id, applications[1].ci_id, RelationshipType.DEPENDS_ON)
    await platform.create_relationship(services[1].ci_id, applications[2].ci_id, RelationshipType.DEPENDS_ON)
    await platform.create_relationship(services[2].ci_id, applications[3].ci_id, RelationshipType.DEPENDS_ON)
    
    # Applications connect to each other
    await platform.create_relationship(applications[1].ci_id, applications[0].ci_id, RelationshipType.CONNECTS_TO)
    await platform.create_relationship(applications[2].ci_id, applications[0].ci_id, RelationshipType.CONNECTS_TO)
    await platform.create_relationship(applications[3].ci_id, applications[0].ci_id, RelationshipType.CONNECTS_TO)
    
    print(f"  🔗 Created {len(platform.relationships)} relationships")
    
    # Create Compliance Policies
    print("\n📋 Creating Compliance Policies...")
    
    policies_data = [
        ("Required OS Version", "All servers must run approved OS version", [CIType.SERVER], ["production"], [
            {"name": "os_check", "attribute": "os", "condition": "exists"}
        ], "high"),
        ("Database Backup", "All databases must have storage configured", [CIType.DATABASE], ["production"], [
            {"name": "storage_check", "attribute": "storage_gb", "condition": "min", "value": 100}
        ], "critical"),
        ("Service Tier", "All services must have tier defined", [CIType.SERVICE], [], [
            {"name": "tier_check", "attribute": "tier", "condition": "exists"}
        ], "medium")
    ]
    
    for name, desc, types, envs, rules, severity in policies_data:
        await platform.create_policy(name, desc, types, envs, rules, severity)
        print(f"  📋 {name} ({severity})")
        
    # Check Compliance
    print("\n✅ Checking Compliance...")
    
    all_violations = []
    for ci in platform.cis.values():
        violations = await platform.check_compliance(ci.ci_id)
        all_violations.extend(violations)
        
    compliant_count = sum(1 for ci in platform.cis.values() if ci.compliance_status == ComplianceStatus.COMPLIANT)
    non_compliant_count = sum(1 for ci in platform.cis.values() if ci.compliance_status == ComplianceStatus.NON_COMPLIANT)
    
    print(f"  ✅ Compliant: {compliant_count}")
    print(f"  ❌ Non-compliant: {non_compliant_count}")
    print(f"  ⚠️ Violations: {len(all_violations)}")
    
    # Run Discovery
    print("\n🔍 Running Discovery...")
    
    discovery = await platform.run_discovery("Cloud Discovery", DiscoverySource.CLOUD_API, ["us-east-1", "us-west-2"])
    print(f"  🔍 Discovered: {discovery.discovered_cis} CIs")
    print(f"  🔄 Updated: {discovery.updated_cis} CIs")
    
    # Impact Analysis
    print("\n💥 Impact Analysis (Database Failure)...")
    
    impact = await platform.analyze_impact(databases[0].ci_id, "failure", 3)
    print(f"  📊 Directly affected: {len(impact.directly_affected)} CIs")
    print(f"  📊 Indirectly affected: {len(impact.indirectly_affected)} CIs")
    print(f"  ⚠️ Critical services: {impact.critical_services_affected}")
    
    # Show affected CIs
    print("\n  Affected CIs:")
    for ci_id in impact.directly_affected:
        ci = platform.cis.get(ci_id)
        if ci:
            print(f"    → {ci.name} ({ci.ci_type.value})")
            
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # CI Dashboard
    print("\n📦 Configuration Items:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Type              │ Environment  │ Status      │ Compliance                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ci in list(platform.cis.values())[:12]:
        name = ci.name[:28].ljust(28)
        ci_type = ci.ci_type.value[:17].ljust(17)
        env = ci.environment[:12].ljust(12)
        status = ci.status.value[:11].ljust(11)
        compliance = ci.compliance_status.value[:100].ljust(100)
        
        print(f"  │ {name} │ {ci_type} │ {env} │ {status} │ {compliance} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Relationships
    print("\n🔗 Sample Relationships:")
    
    for rel in list(platform.relationships.values())[:8]:
        source = platform.cis.get(rel.source_ci_id)
        target = platform.cis.get(rel.target_ci_id)
        if source and target:
            print(f"  {source.name} --[{rel.relationship_type.value}]--> {target.name}")
            
    # Change History
    print("\n📝 Recent Changes:")
    
    for change in platform.change_history[-6:]:
        ci = platform.cis.get(change.ci_id)
        ci_name = ci.name if ci else change.ci_id[:15]
        print(f"  {change.timestamp.strftime('%H:%M:%S')} │ {change.change_type.value:12s} │ {ci_name}")
        
    # Violations
    if all_violations:
        print("\n⚠️ Compliance Violations:")
        for v in all_violations[:5]:
            ci = platform.cis.get(v.ci_id)
            ci_name = ci.name if ci else v.ci_id
            print(f"  [{v.severity.upper()}] {ci_name}: {v.message}")
            
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total CIs: {stats['total_cis']}")
    print(f"  Total Relationships: {stats['total_relationships']}")
    print(f"  Compliance Rate: {metrics.compliance_rate:.1f}%")
    print(f"  Changes (24h): {metrics.changes_last_24h}")
    
    # CIs by Type
    print("\n  CIs by Type:")
    for ci_type, count in stats["by_type"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {ci_type:20s} │ {bar} ({count})")
            
    # CIs by Environment
    print("\n  CIs by Environment:")
    for env, count in stats["by_environment"].items():
        bar = "█" * count
        print(f"    {env:12s} │ {bar} ({count})")
        
    # Relationships by Type
    print("\n  Relationships by Type:")
    for rel_type, count in stats["relationships_by_type"].items():
        if count > 0:
            bar = "█" * count
            print(f"    {rel_type:15s} │ {bar} ({count})")
            
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                          CMDB Platform                             │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total CIs:                     {stats['total_cis']:>12}                      │")
    print(f"│ Active CIs:                    {metrics.active_cis:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Relationships:           {stats['total_relationships']:>12}                      │")
    print(f"│ CI Classes:                    {stats['ci_classes']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliant CIs:                 {metrics.compliant_cis:>12}                      │")
    print(f"│ Non-Compliant CIs:             {metrics.non_compliant_cis:>12}                      │")
    print(f"│ Compliance Rate:               {metrics.compliance_rate:>11.1f}%                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Policies:                      {stats['policies']:>12}                      │")
    print(f"│ Open Violations:               {stats['open_violations']:>12}                      │")
    print(f"│ Change History:                {stats['change_history_count']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("CMDB Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
