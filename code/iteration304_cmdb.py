#!/usr/bin/env python3
"""
Server Init - Iteration 304: CMDB (Configuration Management Database) Platform
Платформа управления конфигурационными единицами

Функционал:
- CI Management - управление конфигурационными единицами
- Relationship Mapping - картирование связей
- Asset Discovery - обнаружение активов
- Change Tracking - отслеживание изменений
- Impact Analysis - анализ влияния
- Compliance Monitoring - мониторинг соответствия
- Audit Trail - аудиторский след
- Federation - федерация с внешними CMDB
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class CIType(Enum):
    """Тип конфигурационной единицы"""
    SERVER = "server"
    DATABASE = "database"
    APPLICATION = "application"
    NETWORK_DEVICE = "network_device"
    STORAGE = "storage"
    CONTAINER = "container"
    SERVICE = "service"
    CLUSTER = "cluster"
    LOAD_BALANCER = "load_balancer"
    FIREWALL = "firewall"


class CIStatus(Enum):
    """Статус CI"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PLANNED = "planned"
    RETIRED = "retired"
    MAINTENANCE = "maintenance"


class RelationshipType(Enum):
    """Тип связи"""
    RUNS_ON = "runs_on"
    DEPENDS_ON = "depends_on"
    CONNECTED_TO = "connected_to"
    HOSTS = "hosts"
    MEMBER_OF = "member_of"
    USES = "uses"
    MANAGED_BY = "managed_by"


class ChangeType(Enum):
    """Тип изменения"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELATIONSHIP_ADD = "relationship_add"
    RELATIONSHIP_REMOVE = "relationship_remove"


class DiscoveryMethod(Enum):
    """Метод обнаружения"""
    MANUAL = "manual"
    AGENT = "agent"
    AGENTLESS = "agentless"
    API = "api"
    IMPORT = "import"


@dataclass
class Attribute:
    """Атрибут CI"""
    name: str
    value: Any
    
    # Metadata
    data_type: str = "string"  # string, number, boolean, date, list
    is_required: bool = False
    is_readonly: bool = False
    
    # Tracking
    last_updated: datetime = field(default_factory=datetime.now)
    source: str = "manual"


@dataclass
class ConfigurationItem:
    """Конфигурационная единица"""
    ci_id: str
    name: str
    ci_type: CIType
    
    # Classification
    class_name: str = ""
    subclass: str = ""
    
    # Status
    status: CIStatus = CIStatus.ACTIVE
    
    # Attributes
    attributes: Dict[str, Attribute] = field(default_factory=dict)
    
    # Relationships
    relationships: List[str] = field(default_factory=list)  # relationship_ids
    
    # Ownership
    owner: str = ""
    team: str = ""
    
    # Location
    location: str = ""
    environment: str = "production"
    
    # Discovery
    discovery_method: DiscoveryMethod = DiscoveryMethod.MANUAL
    last_discovered: Optional[datetime] = None
    
    # Compliance
    compliance_status: str = "compliant"  # compliant, non_compliant, unknown
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """Связь между CI"""
    relationship_id: str
    from_ci_id: str
    to_ci_id: str
    
    # Type
    relationship_type: RelationshipType = RelationshipType.DEPENDS_ON
    
    # Description
    description: str = ""
    
    # Properties
    is_bidirectional: bool = False
    is_critical: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChangeRecord:
    """Запись об изменении"""
    change_id: str
    ci_id: str
    
    # Change
    change_type: ChangeType = ChangeType.UPDATE
    
    # Details
    field_name: str = ""
    old_value: Any = None
    new_value: Any = None
    
    # Source
    changed_by: str = ""
    change_source: str = "manual"
    
    # Reference
    change_request_id: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoveryJob:
    """Задание обнаружения"""
    job_id: str
    name: str
    
    # Target
    target_network: str = ""
    target_type: CIType = CIType.SERVER
    
    # Method
    discovery_method: DiscoveryMethod = DiscoveryMethod.AGENTLESS
    
    # Schedule
    schedule: str = ""  # cron expression
    
    # Status
    status: str = "idle"  # idle, running, completed, failed
    
    # Results
    discovered_count: int = 0
    updated_count: int = 0
    
    # Timestamps
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class ComplianceRule:
    """Правило соответствия"""
    rule_id: str
    name: str
    description: str
    
    # Target
    target_ci_types: List[CIType] = field(default_factory=list)
    
    # Condition
    attribute_name: str = ""
    condition: str = ""  # equals, contains, regex, exists
    expected_value: Any = None
    
    # Severity
    severity: str = "medium"  # low, medium, high, critical
    
    # Status
    enabled: bool = True


@dataclass
class ImpactAnalysis:
    """Анализ влияния"""
    analysis_id: str
    ci_id: str
    
    # Scope
    direction: str = "downstream"  # upstream, downstream, both
    max_depth: int = 3
    
    # Results
    impacted_cis: List[str] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    
    # Metrics
    total_impact: int = 0
    critical_impact: int = 0
    
    # Timestamp
    performed_at: datetime = field(default_factory=datetime.now)


class CMDBManager:
    """Менеджер CMDB"""
    
    def __init__(self):
        self.cis: Dict[str, ConfigurationItem] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.changes: List[ChangeRecord] = []
        self.discovery_jobs: Dict[str, DiscoveryJob] = {}
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        
    async def create_ci(self, name: str, ci_type: CIType,
                       class_name: str = "",
                       environment: str = "production",
                       owner: str = "",
                       team: str = "") -> ConfigurationItem:
        """Создание конфигурационной единицы"""
        ci = ConfigurationItem(
            ci_id=f"ci_{uuid.uuid4().hex[:8]}",
            name=name,
            ci_type=ci_type,
            class_name=class_name,
            environment=environment,
            owner=owner,
            team=team
        )
        
        self.cis[ci.ci_id] = ci
        
        # Record change
        await self._record_change(ci.ci_id, ChangeType.CREATE, "", None, name)
        
        return ci
        
    async def set_attribute(self, ci_id: str, name: str, value: Any,
                           data_type: str = "string") -> bool:
        """Установка атрибута CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return False
            
        old_value = None
        if name in ci.attributes:
            old_value = ci.attributes[name].value
            
        ci.attributes[name] = Attribute(
            name=name,
            value=value,
            data_type=data_type
        )
        
        ci.updated_at = datetime.now()
        
        # Record change
        await self._record_change(ci_id, ChangeType.UPDATE, name, old_value, value)
        
        return True
        
    async def create_relationship(self, from_ci_id: str, to_ci_id: str,
                                 relationship_type: RelationshipType,
                                 is_critical: bool = False) -> Optional[Relationship]:
        """Создание связи между CI"""
        from_ci = self.cis.get(from_ci_id)
        to_ci = self.cis.get(to_ci_id)
        
        if not from_ci or not to_ci:
            return None
            
        relationship = Relationship(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            from_ci_id=from_ci_id,
            to_ci_id=to_ci_id,
            relationship_type=relationship_type,
            is_critical=is_critical
        )
        
        self.relationships[relationship.relationship_id] = relationship
        from_ci.relationships.append(relationship.relationship_id)
        
        # Record change
        await self._record_change(from_ci_id, ChangeType.RELATIONSHIP_ADD,
                                 "relationship", None, f"{relationship_type.value}:{to_ci.name}")
        
        return relationship
        
    async def _record_change(self, ci_id: str, change_type: ChangeType,
                            field_name: str, old_value: Any, new_value: Any):
        """Запись изменения"""
        change = ChangeRecord(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            ci_id=ci_id,
            change_type=change_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )
        
        self.changes.append(change)
        
    async def discover_cis(self, target_type: CIType,
                          count: int = 10) -> List[ConfigurationItem]:
        """Обнаружение конфигурационных единиц"""
        discovered = []
        
        for i in range(count):
            ci = await self.create_ci(
                f"{target_type.value}-{uuid.uuid4().hex[:6]}",
                target_type,
                environment="production" if random.random() > 0.3 else "staging"
            )
            
            ci.discovery_method = DiscoveryMethod.AGENTLESS
            ci.last_discovered = datetime.now()
            
            # Add typical attributes based on type
            if target_type == CIType.SERVER:
                await self.set_attribute(ci.ci_id, "cpu_cores", random.randint(2, 32), "number")
                await self.set_attribute(ci.ci_id, "memory_gb", random.randint(4, 128), "number")
                await self.set_attribute(ci.ci_id, "os", random.choice(["Ubuntu 22.04", "CentOS 8", "Windows Server 2022"]))
                await self.set_attribute(ci.ci_id, "ip_address", f"10.0.{random.randint(1,254)}.{random.randint(1,254)}")
            elif target_type == CIType.DATABASE:
                await self.set_attribute(ci.ci_id, "engine", random.choice(["PostgreSQL", "MySQL", "MongoDB", "Redis"]))
                await self.set_attribute(ci.ci_id, "version", f"{random.randint(10,16)}.{random.randint(0,9)}")
                await self.set_attribute(ci.ci_id, "storage_gb", random.randint(100, 1000), "number")
            elif target_type == CIType.APPLICATION:
                await self.set_attribute(ci.ci_id, "language", random.choice(["Python", "Java", "Node.js", "Go"]))
                await self.set_attribute(ci.ci_id, "version", f"v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,10)}")
                await self.set_attribute(ci.ci_id, "framework", random.choice(["Django", "Spring", "Express", "Gin"]))
                
            discovered.append(ci)
            
        return discovered
        
    async def analyze_impact(self, ci_id: str, direction: str = "downstream",
                            max_depth: int = 3) -> ImpactAnalysis:
        """Анализ влияния изменений"""
        ci = self.cis.get(ci_id)
        
        analysis = ImpactAnalysis(
            analysis_id=f"imp_{uuid.uuid4().hex[:8]}",
            ci_id=ci_id,
            direction=direction,
            max_depth=max_depth
        )
        
        if not ci:
            return analysis
            
        def find_impacted(current_id: str, depth: int, visited: Set[str]) -> List[str]:
            if depth > max_depth or current_id in visited:
                return []
                
            visited.add(current_id)
            impacted = []
            
            for rel in self.relationships.values():
                target_id = None
                
                if direction == "downstream" and rel.from_ci_id == current_id:
                    target_id = rel.to_ci_id
                elif direction == "upstream" and rel.to_ci_id == current_id:
                    target_id = rel.from_ci_id
                elif direction == "both":
                    if rel.from_ci_id == current_id:
                        target_id = rel.to_ci_id
                    elif rel.to_ci_id == current_id:
                        target_id = rel.from_ci_id
                        
                if target_id and target_id not in visited:
                    impacted.append(target_id)
                    impacted.extend(find_impacted(target_id, depth + 1, visited.copy()))
                    
                    if rel.is_critical:
                        analysis.critical_impact += 1
                        if target_id not in analysis.critical_path:
                            analysis.critical_path.append(target_id)
                            
            return impacted
            
        analysis.impacted_cis = list(set(find_impacted(ci_id, 0, set())))
        analysis.total_impact = len(analysis.impacted_cis)
        
        return analysis
        
    async def check_compliance(self) -> Dict[str, List[Dict[str, Any]]]:
        """Проверка соответствия правилам"""
        violations = {}
        
        for rule in self.compliance_rules.values():
            if not rule.enabled:
                continue
                
            rule_violations = []
            
            for ci in self.cis.values():
                if rule.target_ci_types and ci.ci_type not in rule.target_ci_types:
                    continue
                    
                # Check attribute
                attr = ci.attributes.get(rule.attribute_name)
                
                is_compliant = True
                
                if rule.condition == "exists":
                    is_compliant = attr is not None
                elif rule.condition == "equals" and attr:
                    is_compliant = attr.value == rule.expected_value
                elif rule.condition == "contains" and attr:
                    is_compliant = rule.expected_value in str(attr.value)
                    
                if not is_compliant:
                    rule_violations.append({
                        "ci_id": ci.ci_id,
                        "ci_name": ci.name,
                        "rule_name": rule.name,
                        "severity": rule.severity
                    })
                    ci.compliance_status = "non_compliant"
                    
            if rule_violations:
                violations[rule.rule_id] = rule_violations
                
        return violations
        
    async def create_compliance_rule(self, name: str, description: str,
                                    target_types: List[CIType],
                                    attribute: str,
                                    condition: str,
                                    expected_value: Any = None,
                                    severity: str = "medium") -> ComplianceRule:
        """Создание правила соответствия"""
        rule = ComplianceRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            target_ci_types=target_types,
            attribute_name=attribute,
            condition=condition,
            expected_value=expected_value,
            severity=severity
        )
        
        self.compliance_rules[rule.rule_id] = rule
        return rule
        
    def get_ci_details(self, ci_id: str) -> Dict[str, Any]:
        """Получение деталей CI"""
        ci = self.cis.get(ci_id)
        if not ci:
            return {}
            
        # Get relationships
        outbound = []
        inbound = []
        
        for rel in self.relationships.values():
            if rel.from_ci_id == ci_id:
                to_ci = self.cis.get(rel.to_ci_id)
                outbound.append({
                    "type": rel.relationship_type.value,
                    "target": to_ci.name if to_ci else "Unknown",
                    "critical": rel.is_critical
                })
            elif rel.to_ci_id == ci_id:
                from_ci = self.cis.get(rel.from_ci_id)
                inbound.append({
                    "type": rel.relationship_type.value,
                    "source": from_ci.name if from_ci else "Unknown",
                    "critical": rel.is_critical
                })
                
        # Get recent changes
        recent_changes = [
            c for c in self.changes[-50:]
            if c.ci_id == ci_id
        ][-5:]
        
        return {
            "ci_id": ci_id,
            "name": ci.name,
            "type": ci.ci_type.value,
            "class": ci.class_name,
            "status": ci.status.value,
            "environment": ci.environment,
            "owner": ci.owner,
            "team": ci.team,
            "attributes": {k: v.value for k, v in ci.attributes.items()},
            "outbound_relationships": outbound,
            "inbound_relationships": inbound,
            "compliance_status": ci.compliance_status,
            "discovery_method": ci.discovery_method.value,
            "last_discovered": ci.last_discovered.isoformat() if ci.last_discovered else None,
            "recent_changes": len(recent_changes),
            "created_at": ci.created_at.isoformat()
        }
        
    def search_cis(self, query: str = "", ci_type: Optional[CIType] = None,
                  status: Optional[CIStatus] = None,
                  environment: str = "") -> List[ConfigurationItem]:
        """Поиск конфигурационных единиц"""
        results = []
        
        for ci in self.cis.values():
            if ci_type and ci.ci_type != ci_type:
                continue
                
            if status and ci.status != status:
                continue
                
            if environment and ci.environment != environment:
                continue
                
            if query:
                query_lower = query.lower()
                if (query_lower not in ci.name.lower() and
                    query_lower not in ci.class_name.lower()):
                    # Check attributes
                    found = False
                    for attr in ci.attributes.values():
                        if query_lower in str(attr.value).lower():
                            found = True
                            break
                    if not found:
                        continue
                        
            results.append(ci)
            
        return results
        
    def get_change_history(self, ci_id: str, limit: int = 50) -> List[ChangeRecord]:
        """История изменений CI"""
        return [c for c in self.changes if c.ci_id == ci_id][-limit:]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика CMDB"""
        by_type = {}
        by_status = {}
        by_environment = {}
        compliant = 0
        non_compliant = 0
        
        for ci in self.cis.values():
            by_type[ci.ci_type.value] = by_type.get(ci.ci_type.value, 0) + 1
            by_status[ci.status.value] = by_status.get(ci.status.value, 0) + 1
            by_environment[ci.environment] = by_environment.get(ci.environment, 0) + 1
            
            if ci.compliance_status == "compliant":
                compliant += 1
            else:
                non_compliant += 1
                
        rel_by_type = {}
        for rel in self.relationships.values():
            rel_by_type[rel.relationship_type.value] = rel_by_type.get(rel.relationship_type.value, 0) + 1
            
        return {
            "total_cis": len(self.cis),
            "by_type": by_type,
            "by_status": by_status,
            "by_environment": by_environment,
            "total_relationships": len(self.relationships),
            "relationships_by_type": rel_by_type,
            "total_changes": len(self.changes),
            "compliance_rules": len(self.compliance_rules),
            "compliant_cis": compliant,
            "non_compliant_cis": non_compliant
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 304: CMDB Platform")
    print("=" * 60)
    
    manager = CMDBManager()
    print("✓ CMDB Manager created")
    
    # Create CIs manually
    print("\n📦 Creating Configuration Items...")
    
    # Infrastructure CIs
    infra_cis = []
    
    # Servers
    for i in range(4):
        ci = await manager.create_ci(f"web-server-{i+1}", CIType.SERVER, "Linux Server", "production", "ops-team", "Infrastructure")
        await manager.set_attribute(ci.ci_id, "cpu_cores", 8, "number")
        await manager.set_attribute(ci.ci_id, "memory_gb", 32, "number")
        await manager.set_attribute(ci.ci_id, "os", "Ubuntu 22.04")
        await manager.set_attribute(ci.ci_id, "ip_address", f"10.0.1.{10+i}")
        infra_cis.append(ci)
        print(f"  🖥️ {ci.name} (Server)")
        
    # Databases
    db_cis = []
    for db_name in ["primary-db", "replica-db", "analytics-db"]:
        ci = await manager.create_ci(db_name, CIType.DATABASE, "PostgreSQL", "production", "dba-team", "Data")
        await manager.set_attribute(ci.ci_id, "engine", "PostgreSQL")
        await manager.set_attribute(ci.ci_id, "version", "15.2")
        await manager.set_attribute(ci.ci_id, "storage_gb", 500, "number")
        db_cis.append(ci)
        print(f"  🗄️ {ci.name} (Database)")
        
    # Applications
    app_cis = []
    apps_data = [
        ("user-service", "Python", "Django"),
        ("order-service", "Java", "Spring"),
        ("payment-service", "Go", "Gin"),
        ("notification-service", "Node.js", "Express")
    ]
    
    for app_name, lang, framework in apps_data:
        ci = await manager.create_ci(app_name, CIType.APPLICATION, "Microservice", "production", "dev-team", "Application")
        await manager.set_attribute(ci.ci_id, "language", lang)
        await manager.set_attribute(ci.ci_id, "framework", framework)
        await manager.set_attribute(ci.ci_id, "version", f"v{random.randint(1,3)}.{random.randint(0,10)}.0")
        app_cis.append(ci)
        print(f"  📱 {ci.name} (Application)")
        
    # Load Balancer
    lb_ci = await manager.create_ci("main-lb", CIType.LOAD_BALANCER, "HAProxy", "production", "ops-team", "Infrastructure")
    await manager.set_attribute(lb_ci.ci_id, "algorithm", "round-robin")
    await manager.set_attribute(lb_ci.ci_id, "max_connections", 10000, "number")
    print(f"  ⚖️ {lb_ci.name} (Load Balancer)")
    
    # Discover more CIs
    print("\n🔍 Discovering Additional CIs...")
    
    discovered_servers = await manager.discover_cis(CIType.SERVER, 5)
    print(f"  ✓ Discovered {len(discovered_servers)} servers")
    
    discovered_containers = await manager.discover_cis(CIType.CONTAINER, 8)
    print(f"  ✓ Discovered {len(discovered_containers)} containers")
    
    # Create relationships
    print("\n🔗 Creating Relationships...")
    
    # Apps run on servers
    for i, app in enumerate(app_cis):
        server = infra_cis[i % len(infra_cis)]
        await manager.create_relationship(app.ci_id, server.ci_id, RelationshipType.RUNS_ON, True)
        
    # Apps depend on databases
    for app in app_cis:
        await manager.create_relationship(app.ci_id, db_cis[0].ci_id, RelationshipType.DEPENDS_ON, True)
        
    # Load balancer hosts apps
    for app in app_cis:
        await manager.create_relationship(lb_ci.ci_id, app.ci_id, RelationshipType.HOSTS, True)
        
    # Database replication
    await manager.create_relationship(db_cis[1].ci_id, db_cis[0].ci_id, RelationshipType.DEPENDS_ON, True)
    
    print(f"  ✓ Created {len(manager.relationships)} relationships")
    
    # Create compliance rules
    print("\n📋 Creating Compliance Rules...")
    
    rules_data = [
        ("OS Version Check", "All servers must run approved OS", [CIType.SERVER], "os", "contains", "Ubuntu", "high"),
        ("Database Engine Check", "All DBs must use PostgreSQL", [CIType.DATABASE], "engine", "equals", "PostgreSQL", "critical"),
        ("Memory Minimum", "Servers must have minimum RAM", [CIType.SERVER], "memory_gb", "exists", None, "medium"),
        ("Version Tracking", "Applications must have version", [CIType.APPLICATION], "version", "exists", None, "low")
    ]
    
    for name, desc, types, attr, cond, val, sev in rules_data:
        rule = await manager.create_compliance_rule(name, desc, types, attr, cond, val, sev)
        print(f"  📋 {name} ({sev})")
        
    # Check compliance
    print("\n✅ Checking Compliance...")
    
    violations = await manager.check_compliance()
    
    total_violations = sum(len(v) for v in violations.values())
    print(f"  Found {total_violations} violations across {len(violations)} rules")
    
    for rule_id, viols in list(violations.items())[:3]:
        rule = manager.compliance_rules.get(rule_id)
        if rule:
            print(f"\n  ⚠️ {rule.name} ({len(viols)} violations)")
            for v in viols[:2]:
                print(f"     - {v['ci_name']}")
                
    # Impact analysis
    print("\n🎯 Impact Analysis:")
    
    for ci in [db_cis[0], lb_ci]:
        analysis = await manager.analyze_impact(ci.ci_id, "both", 3)
        
        print(f"\n  🎯 {ci.name}:")
        print(f"     Total Impact: {analysis.total_impact} CIs")
        print(f"     Critical Impact: {analysis.critical_impact} CIs")
        
        if analysis.impacted_cis[:3]:
            print(f"     Impacted CIs:")
            for imp_ci_id in analysis.impacted_cis[:3]:
                imp_ci = manager.cis.get(imp_ci_id)
                if imp_ci:
                    print(f"       - {imp_ci.name}")
                    
    # CI Details
    print("\n📋 CI Details:")
    
    for ci in app_cis[:2]:
        details = manager.get_ci_details(ci.ci_id)
        
        print(f"\n  📋 {details['name']}")
        print(f"     Type: {details['type']} | Class: {details['class']}")
        print(f"     Environment: {details['environment']}")
        print(f"     Compliance: {details['compliance_status']}")
        
        if details['attributes']:
            print(f"     Attributes:")
            for k, v in list(details['attributes'].items())[:3]:
                print(f"       {k}: {v}")
                
        if details['outbound_relationships']:
            print(f"     Outbound Relationships:")
            for rel in details['outbound_relationships'][:2]:
                critical = "🔴" if rel['critical'] else "🟢"
                print(f"       {critical} {rel['type']} → {rel['target']}")
                
    # Search CIs
    print("\n🔍 Search Results:")
    
    # By type
    servers = manager.search_cis(ci_type=CIType.SERVER)
    print(f"  Servers: {len(servers)}")
    
    # By environment
    prod_cis = manager.search_cis(environment="production")
    print(f"  Production CIs: {len(prod_cis)}")
    
    # By query
    python_apps = manager.search_cis(query="Python")
    print(f"  Python-related: {len(python_apps)}")
    
    # Change history
    print("\n📜 Change History (primary-db):")
    
    history = manager.get_change_history(db_cis[0].ci_id, 10)
    
    for change in history[:5]:
        print(f"  {change.timestamp.strftime('%H:%M:%S')} - {change.change_type.value}: {change.field_name}")
        
    # CI Inventory
    print("\n📊 CI Inventory:")
    
    print("\n  ┌────────────────────────────┬──────────────────┬──────────┬─────────────┐")
    print("  │ Name                       │ Type             │ Status   │ Compliance  │")
    print("  ├────────────────────────────┼──────────────────┼──────────┼─────────────┤")
    
    all_cis = list(manager.cis.values())[:15]
    for ci in all_cis:
        name = ci.name[:26].ljust(26)
        ci_type = ci.ci_type.value[:16].ljust(16)
        
        status_icons = {"active": "🟢", "inactive": "⚪", "maintenance": "🟠", "retired": "🔴", "planned": "🔵"}
        status = f"{status_icons.get(ci.status.value, '⚪')} {ci.status.value[:6]}".ljust(8)
        
        comp_icons = {"compliant": "✅", "non_compliant": "❌", "unknown": "⚪"}
        compliance = f"{comp_icons.get(ci.compliance_status, '⚪')} {ci.compliance_status[:9]}".ljust(11)
        
        print(f"  │ {name} │ {ci_type} │ {status} │ {compliance} │")
        
    print("  └────────────────────────────┴──────────────────┴──────────┴─────────────┘")
    
    # Statistics
    print("\n📊 CMDB Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total CIs: {stats['total_cis']}")
    
    print("\n  By Type:")
    for ci_type, count in stats['by_type'].items():
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        print(f"    {ci_type:20} [{bar}] {count}")
        
    print(f"\n  By Environment:")
    for env, count in stats['by_environment'].items():
        print(f"    {env}: {count}")
        
    print(f"\n  Total Relationships: {stats['total_relationships']}")
    print(f"  Total Changes: {stats['total_changes']}")
    print(f"  Compliance Rules: {stats['compliance_rules']}")
    print(f"  Compliant CIs: {stats['compliant_cis']}")
    print(f"  Non-Compliant CIs: {stats['non_compliant_cis']}")
    
    compliance_rate = (stats['compliant_cis'] / max(stats['total_cis'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                        CMDB Dashboard                               │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Configuration Items:  {stats['total_cis']:>12}                          │")
    print(f"│ Total Relationships:        {stats['total_relationships']:>12}                          │")
    print(f"│ Total Changes Tracked:      {stats['total_changes']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliance Rate:            {compliance_rate:>11.1f}%                          │")
    print(f"│ Non-Compliant CIs:          {stats['non_compliant_cis']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("CMDB Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
