#!/usr/bin/env python3
"""
Server Init - Iteration 153: Resource Tagging Platform
Платформа тегирования ресурсов

Функционал:
- Tag Management - управление тегами
- Policy Enforcement - применение политик
- Tag Inheritance - наследование тегов
- Compliance Checking - проверка соответствия
- Cost Allocation - распределение затрат
- Resource Discovery - обнаружение ресурсов
- Tag Automation - автоматизация тегирования
- Reporting - отчётность
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import re
from collections import defaultdict


class ResourceType(Enum):
    """Тип ресурса"""
    EC2_INSTANCE = "ec2_instance"
    RDS_DATABASE = "rds_database"
    S3_BUCKET = "s3_bucket"
    LAMBDA_FUNCTION = "lambda_function"
    EKS_CLUSTER = "eks_cluster"
    ECS_SERVICE = "ecs_service"
    LOAD_BALANCER = "load_balancer"
    VPC = "vpc"
    SUBNET = "subnet"
    SECURITY_GROUP = "security_group"


class TagStatus(Enum):
    """Статус тега"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    MISSING = "missing"
    INVALID = "invalid"


class PolicyAction(Enum):
    """Действие политики"""
    REQUIRE = "require"
    RECOMMEND = "recommend"
    PROHIBIT = "prohibit"
    AUTO_TAG = "auto_tag"


class ComplianceLevel(Enum):
    """Уровень соответствия"""
    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"


@dataclass
class Tag:
    """Тег"""
    key: str
    value: str
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # Inheritance
    inherited: bool = False
    inherited_from: str = ""


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    name: str = ""
    
    # Type
    resource_type: ResourceType = ResourceType.EC2_INSTANCE
    
    # Tags
    tags: Dict[str, Tag] = field(default_factory=dict)
    
    # Hierarchy
    parent_id: str = ""
    
    # Cloud info
    region: str = ""
    account_id: str = ""
    arn: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    
    # Compliance
    compliance_status: ComplianceLevel = ComplianceLevel.NON_COMPLIANT
    missing_tags: List[str] = field(default_factory=list)


@dataclass
class TagPolicy:
    """Политика тегирования"""
    policy_id: str
    name: str = ""
    
    # Scope
    resource_types: List[ResourceType] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    accounts: List[str] = field(default_factory=list)
    
    # Rules
    rules: List[Dict] = field(default_factory=list)
    
    # Status
    enabled: bool = True
    
    # Statistics
    compliant_resources: int = 0
    non_compliant_resources: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TagRule:
    """Правило тегирования"""
    rule_id: str
    tag_key: str = ""
    
    # Action
    action: PolicyAction = PolicyAction.REQUIRE
    
    # Validation
    allowed_values: List[str] = field(default_factory=list)
    pattern: str = ""  # Regex pattern
    
    # Default
    default_value: str = ""
    
    # Description
    description: str = ""


@dataclass
class ComplianceReport:
    """Отчёт о соответствии"""
    report_id: str
    
    # Scope
    policy_id: str = ""
    
    # Results
    total_resources: int = 0
    compliant_count: int = 0
    non_compliant_count: int = 0
    
    # Details
    violations: List[Dict] = field(default_factory=list)
    
    # Metrics
    compliance_percentage: float = 0.0
    
    # Timestamp
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostAllocation:
    """Распределение затрат"""
    allocation_id: str
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Allocations
    by_tag: Dict[str, Dict[str, float]] = field(default_factory=dict)  # tag_key -> {tag_value -> cost}
    
    # Total
    total_cost: float = 0.0
    untagged_cost: float = 0.0


@dataclass
class TagTemplate:
    """Шаблон тегов"""
    template_id: str
    name: str = ""
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Scope
    resource_types: List[ResourceType] = field(default_factory=list)
    
    # Auto-apply
    auto_apply: bool = False
    
    # Description
    description: str = ""


@dataclass
class InheritanceRule:
    """Правило наследования"""
    rule_id: str
    name: str = ""
    
    # Parent-child
    parent_type: ResourceType = ResourceType.VPC
    child_type: ResourceType = ResourceType.EC2_INSTANCE
    
    # Tags to inherit
    tags_to_inherit: List[str] = field(default_factory=list)
    inherit_all: bool = False
    
    # Status
    enabled: bool = True


class TagManager:
    """Менеджер тегов"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        
    def add_resource(self, name: str, resource_type: ResourceType,
                      tags: Dict[str, str] = None, **kwargs) -> Resource:
        """Добавление ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            **kwargs
        )
        
        if tags:
            for key, value in tags.items():
                resource.tags[key] = Tag(key=key, value=value)
                
        self.resources[resource.resource_id] = resource
        return resource
        
    def add_tag(self, resource_id: str, key: str, value: str,
                 created_by: str = "") -> bool:
        """Добавление тега"""
        resource = self.resources.get(resource_id)
        if not resource:
            return False
            
        resource.tags[key] = Tag(
            key=key,
            value=value,
            created_by=created_by
        )
        return True
        
    def remove_tag(self, resource_id: str, key: str) -> bool:
        """Удаление тега"""
        resource = self.resources.get(resource_id)
        if not resource or key not in resource.tags:
            return False
            
        del resource.tags[key]
        return True
        
    def update_tag(self, resource_id: str, key: str, value: str) -> bool:
        """Обновление тега"""
        resource = self.resources.get(resource_id)
        if not resource or key not in resource.tags:
            return False
            
        resource.tags[key].value = value
        return True
        
    def get_resources_by_tag(self, key: str, value: str = None) -> List[Resource]:
        """Поиск ресурсов по тегу"""
        results = []
        for resource in self.resources.values():
            if key in resource.tags:
                if value is None or resource.tags[key].value == value:
                    results.append(resource)
        return results
        
    def bulk_tag(self, resource_ids: List[str], tags: Dict[str, str],
                  created_by: str = "") -> int:
        """Массовое тегирование"""
        tagged = 0
        for rid in resource_ids:
            for key, value in tags.items():
                if self.add_tag(rid, key, value, created_by):
                    tagged += 1
        return tagged


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self, tag_manager: TagManager):
        self.tag_manager = tag_manager
        self.policies: Dict[str, TagPolicy] = {}
        
    def create_policy(self, name: str, rules: List[Dict],
                       resource_types: List[ResourceType] = None,
                       **kwargs) -> TagPolicy:
        """Создание политики"""
        policy = TagPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            rules=rules,
            resource_types=resource_types or [],
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def evaluate_resource(self, resource: Resource, policy: TagPolicy) -> Dict:
        """Оценка ресурса по политике"""
        result = {
            "compliant": True,
            "violations": [],
            "missing_tags": [],
            "invalid_tags": []
        }
        
        # Check if policy applies to this resource type
        if policy.resource_types and resource.resource_type not in policy.resource_types:
            return result
            
        for rule in policy.rules:
            tag_key = rule.get("tag_key")
            action = rule.get("action", "require")
            
            if action == "require":
                if tag_key not in resource.tags:
                    result["compliant"] = False
                    result["missing_tags"].append(tag_key)
                    result["violations"].append({
                        "rule": tag_key,
                        "type": "missing",
                        "message": f"Required tag '{tag_key}' is missing"
                    })
                else:
                    # Validate value if rules exist
                    allowed = rule.get("allowed_values", [])
                    pattern = rule.get("pattern")
                    value = resource.tags[tag_key].value
                    
                    if allowed and value not in allowed:
                        result["compliant"] = False
                        result["invalid_tags"].append(tag_key)
                        result["violations"].append({
                            "rule": tag_key,
                            "type": "invalid_value",
                            "message": f"Tag '{tag_key}' value '{value}' not in allowed values"
                        })
                        
                    if pattern and not re.match(pattern, value):
                        result["compliant"] = False
                        result["invalid_tags"].append(tag_key)
                        result["violations"].append({
                            "rule": tag_key,
                            "type": "pattern_mismatch",
                            "message": f"Tag '{tag_key}' value doesn't match pattern"
                        })
                        
            elif action == "prohibit":
                if tag_key in resource.tags:
                    result["compliant"] = False
                    result["violations"].append({
                        "rule": tag_key,
                        "type": "prohibited",
                        "message": f"Prohibited tag '{tag_key}' is present"
                    })
                    
        return result
        
    def evaluate_all(self, policy_id: str = None) -> ComplianceReport:
        """Оценка всех ресурсов"""
        report = ComplianceReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id or "all"
        )
        
        policies = [self.policies[policy_id]] if policy_id else list(self.policies.values())
        
        for resource in self.tag_manager.resources.values():
            all_compliant = True
            
            for policy in policies:
                result = self.evaluate_resource(resource, policy)
                
                if not result["compliant"]:
                    all_compliant = False
                    for violation in result["violations"]:
                        report.violations.append({
                            "resource_id": resource.resource_id,
                            "resource_name": resource.name,
                            "resource_type": resource.resource_type.value,
                            **violation
                        })
                        
            if all_compliant:
                report.compliant_count += 1
                resource.compliance_status = ComplianceLevel.FULL
            else:
                report.non_compliant_count += 1
                resource.compliance_status = ComplianceLevel.NON_COMPLIANT
                
            report.total_resources += 1
            
        if report.total_resources > 0:
            report.compliance_percentage = (
                report.compliant_count / report.total_resources * 100
            )
            
        return report


class InheritanceEngine:
    """Движок наследования"""
    
    def __init__(self, tag_manager: TagManager):
        self.tag_manager = tag_manager
        self.rules: Dict[str, InheritanceRule] = {}
        
    def add_rule(self, name: str, parent_type: ResourceType,
                  child_type: ResourceType, tags_to_inherit: List[str],
                  **kwargs) -> InheritanceRule:
        """Добавление правила"""
        rule = InheritanceRule(
            rule_id=f"inh_{uuid.uuid4().hex[:8]}",
            name=name,
            parent_type=parent_type,
            child_type=child_type,
            tags_to_inherit=tags_to_inherit,
            **kwargs
        )
        self.rules[rule.rule_id] = rule
        return rule
        
    def apply_inheritance(self) -> int:
        """Применение наследования"""
        inherited_count = 0
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            # Find parents and children
            parents = [r for r in self.tag_manager.resources.values() 
                       if r.resource_type == rule.parent_type]
            children = [r for r in self.tag_manager.resources.values()
                        if r.resource_type == rule.child_type]
                        
            for child in children:
                parent = self._find_parent(child, parents)
                if not parent:
                    continue
                    
                tags_to_inherit = (
                    list(parent.tags.keys()) if rule.inherit_all
                    else rule.tags_to_inherit
                )
                
                for tag_key in tags_to_inherit:
                    if tag_key in parent.tags and tag_key not in child.tags:
                        inherited_tag = Tag(
                            key=tag_key,
                            value=parent.tags[tag_key].value,
                            inherited=True,
                            inherited_from=parent.resource_id
                        )
                        child.tags[tag_key] = inherited_tag
                        inherited_count += 1
                        
        return inherited_count
        
    def _find_parent(self, child: Resource, parents: List[Resource]) -> Optional[Resource]:
        """Поиск родителя"""
        if child.parent_id:
            return self.tag_manager.resources.get(child.parent_id)
            
        # Simple matching by region/account
        for parent in parents:
            if parent.region == child.region and parent.account_id == child.account_id:
                return parent
                
        return None


class CostAllocationEngine:
    """Движок распределения затрат"""
    
    def __init__(self, tag_manager: TagManager):
        self.tag_manager = tag_manager
        
    def allocate_costs(self, costs: Dict[str, float],
                        allocation_tag: str) -> CostAllocation:
        """Распределение затрат"""
        allocation = CostAllocation(
            allocation_id=f"alloc_{uuid.uuid4().hex[:8]}"
        )
        
        tag_costs: Dict[str, float] = defaultdict(float)
        untagged = 0.0
        
        for resource_id, cost in costs.items():
            resource = self.tag_manager.resources.get(resource_id)
            
            if resource and allocation_tag in resource.tags:
                tag_value = resource.tags[allocation_tag].value
                tag_costs[tag_value] += cost
            else:
                untagged += cost
                
            allocation.total_cost += cost
            
        allocation.by_tag[allocation_tag] = dict(tag_costs)
        allocation.untagged_cost = untagged
        
        return allocation
        
    def generate_cost_report(self, allocation: CostAllocation,
                              tag_key: str) -> Dict:
        """Генерация отчёта о затратах"""
        report = {
            "tag_key": tag_key,
            "total_cost": allocation.total_cost,
            "untagged_cost": allocation.untagged_cost,
            "untagged_percentage": (
                allocation.untagged_cost / allocation.total_cost * 100
                if allocation.total_cost > 0 else 0
            ),
            "breakdown": []
        }
        
        if tag_key in allocation.by_tag:
            for value, cost in sorted(
                allocation.by_tag[tag_key].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report["breakdown"].append({
                    "value": value,
                    "cost": cost,
                    "percentage": cost / allocation.total_cost * 100 if allocation.total_cost > 0 else 0
                })
                
        return report


class TemplateManager:
    """Менеджер шаблонов"""
    
    def __init__(self, tag_manager: TagManager):
        self.tag_manager = tag_manager
        self.templates: Dict[str, TagTemplate] = {}
        
    def create_template(self, name: str, tags: Dict[str, str],
                         **kwargs) -> TagTemplate:
        """Создание шаблона"""
        template = TagTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            tags=tags,
            **kwargs
        )
        self.templates[template.template_id] = template
        return template
        
    def apply_template(self, template_id: str, resource_ids: List[str],
                        created_by: str = "") -> int:
        """Применение шаблона"""
        template = self.templates.get(template_id)
        if not template:
            return 0
            
        return self.tag_manager.bulk_tag(resource_ids, template.tags, created_by)


class ResourceTaggingPlatform:
    """Платформа тегирования ресурсов"""
    
    def __init__(self):
        self.tag_manager = TagManager()
        self.policy_engine = PolicyEngine(self.tag_manager)
        self.inheritance_engine = InheritanceEngine(self.tag_manager)
        self.cost_engine = CostAllocationEngine(self.tag_manager)
        self.template_manager = TemplateManager(self.tag_manager)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        resources = list(self.tag_manager.resources.values())
        
        total_tags = sum(len(r.tags) for r in resources)
        compliant = len([r for r in resources 
                         if r.compliance_status == ComplianceLevel.FULL])
                         
        # Tag coverage
        tag_coverage: Dict[str, int] = defaultdict(int)
        for resource in resources:
            for tag_key in resource.tags:
                tag_coverage[tag_key] += 1
                
        return {
            "total_resources": len(resources),
            "total_tags": total_tags,
            "avg_tags_per_resource": total_tags / len(resources) if resources else 0,
            "compliant_resources": compliant,
            "compliance_rate": compliant / len(resources) * 100 if resources else 0,
            "policies": len(self.policy_engine.policies),
            "templates": len(self.template_manager.templates),
            "inheritance_rules": len(self.inheritance_engine.rules),
            "tag_coverage": dict(tag_coverage)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 153: Resource Tagging Platform")
    print("=" * 60)
    
    async def demo():
        platform = ResourceTaggingPlatform()
        print("✓ Resource Tagging Platform created")
        
        # Add resources
        print("\n📦 Adding Resources...")
        
        resources_data = [
            ("web-server-1", ResourceType.EC2_INSTANCE, {"Environment": "production", "Team": "platform"}),
            ("web-server-2", ResourceType.EC2_INSTANCE, {"Environment": "production", "Team": "platform"}),
            ("api-server-1", ResourceType.EC2_INSTANCE, {"Environment": "production"}),
            ("dev-server-1", ResourceType.EC2_INSTANCE, {"Environment": "development", "Team": "dev"}),
            ("main-db", ResourceType.RDS_DATABASE, {"Environment": "production", "Team": "data", "Backup": "daily"}),
            ("cache-db", ResourceType.RDS_DATABASE, {"Environment": "production"}),
            ("logs-bucket", ResourceType.S3_BUCKET, {"Environment": "production", "Compliance": "pci"}),
            ("backups-bucket", ResourceType.S3_BUCKET, {"Environment": "production"}),
            ("process-func", ResourceType.LAMBDA_FUNCTION, {"Environment": "production", "Team": "platform"}),
            ("main-vpc", ResourceType.VPC, {"Environment": "production", "Team": "network", "CostCenter": "IT001"}),
            ("web-subnet", ResourceType.SUBNET, {"Environment": "production"}),
        ]
        
        for name, rtype, tags in resources_data:
            resource = platform.tag_manager.add_resource(
                name, rtype, tags,
                region="us-east-1",
                account_id="123456789012"
            )
            tag_list = ", ".join(f"{k}={v}" for k, v in tags.items())
            print(f"  ✓ {name} ({rtype.value}): {tag_list}")
            
        # Create tagging policies
        print("\n📋 Creating Tagging Policies...")
        
        # Required tags policy
        required_policy = platform.policy_engine.create_policy(
            "Required Tags Policy",
            rules=[
                {
                    "tag_key": "Environment",
                    "action": "require",
                    "allowed_values": ["production", "staging", "development", "qa"]
                },
                {
                    "tag_key": "Team",
                    "action": "require"
                },
                {
                    "tag_key": "CostCenter",
                    "action": "require",
                    "pattern": r"^[A-Z]{2}\d{3}$"
                }
            ],
            resource_types=[ResourceType.EC2_INSTANCE, ResourceType.RDS_DATABASE]
        )
        print(f"  ✓ {required_policy.name}: {len(required_policy.rules)} rules")
        
        # Security policy
        security_policy = platform.policy_engine.create_policy(
            "Security Tags Policy",
            rules=[
                {
                    "tag_key": "Compliance",
                    "action": "require",
                    "allowed_values": ["pci", "hipaa", "sox", "gdpr"]
                }
            ],
            resource_types=[ResourceType.S3_BUCKET]
        )
        print(f"  ✓ {security_policy.name}: {len(security_policy.rules)} rules")
        
        # Create tag templates
        print("\n📝 Creating Tag Templates...")
        
        templates_data = [
            ("Production Standard", {
                "Environment": "production",
                "ManagedBy": "terraform",
                "BackupPolicy": "standard"
            }),
            ("Development Standard", {
                "Environment": "development",
                "ManagedBy": "terraform",
                "AutoShutdown": "true"
            }),
            ("Compliance PCI", {
                "Compliance": "pci",
                "DataClassification": "confidential",
                "Encryption": "required"
            })
        ]
        
        for name, tags in templates_data:
            template = platform.template_manager.create_template(name, tags)
            print(f"  ✓ {name}: {len(tags)} tags")
            
        # Add inheritance rules
        print("\n🔗 Creating Inheritance Rules...")
        
        rule = platform.inheritance_engine.add_rule(
            "VPC to EC2 Inheritance",
            parent_type=ResourceType.VPC,
            child_type=ResourceType.EC2_INSTANCE,
            tags_to_inherit=["CostCenter", "Team"]
        )
        print(f"  ✓ {rule.name}")
        
        rule2 = platform.inheritance_engine.add_rule(
            "VPC to Subnet Inheritance",
            parent_type=ResourceType.VPC,
            child_type=ResourceType.SUBNET,
            tags_to_inherit=["Environment", "CostCenter"],
        )
        print(f"  ✓ {rule2.name}")
        
        # Apply inheritance
        print("\n🔄 Applying Tag Inheritance...")
        
        # Set parent relationships
        vpc = next((r for r in platform.tag_manager.resources.values() 
                    if r.resource_type == ResourceType.VPC), None)
        if vpc:
            for resource in platform.tag_manager.resources.values():
                if resource.resource_type in [ResourceType.EC2_INSTANCE, ResourceType.SUBNET]:
                    resource.parent_id = vpc.resource_id
                    
        inherited = platform.inheritance_engine.apply_inheritance()
        print(f"  ✓ Inherited {inherited} tags")
        
        # Run compliance check
        print("\n✅ Running Compliance Check...")
        
        report = platform.policy_engine.evaluate_all()
        
        print(f"\n  Total Resources: {report.total_resources}")
        print(f"  Compliant: {report.compliant_count}")
        print(f"  Non-Compliant: {report.non_compliant_count}")
        print(f"  Compliance Rate: {report.compliance_percentage:.1f}%")
        
        # Show violations
        if report.violations:
            print(f"\n  Violations ({len(report.violations)}):")
            violation_summary = defaultdict(int)
            for v in report.violations:
                violation_summary[v["rule"]] += 1
                
            for tag, count in sorted(violation_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {tag}: {count} resources")
                
        # Cost allocation
        print("\n💰 Cost Allocation by Tag...")
        
        # Simulate costs
        costs = {}
        import random
        for resource in platform.tag_manager.resources.values():
            costs[resource.resource_id] = random.uniform(50, 500)
            
        allocation = platform.cost_engine.allocate_costs(costs, "Team")
        cost_report = platform.cost_engine.generate_cost_report(allocation, "Team")
        
        print(f"\n  Total Cost: ${cost_report['total_cost']:,.2f}")
        print(f"  Untagged: ${cost_report['untagged_cost']:,.2f} ({cost_report['untagged_percentage']:.1f}%)")
        
        print("\n  By Team:")
        for item in cost_report["breakdown"]:
            bar = "█" * int(item["percentage"] / 5)
            print(f"    {item['value']:15}: ${item['cost']:>8,.2f} ({item['percentage']:5.1f}%) {bar}")
            
        # Allocation by Environment
        env_allocation = platform.cost_engine.allocate_costs(costs, "Environment")
        env_report = platform.cost_engine.generate_cost_report(env_allocation, "Environment")
        
        print("\n  By Environment:")
        for item in env_report["breakdown"]:
            bar = "█" * int(item["percentage"] / 5)
            print(f"    {item['value']:15}: ${item['cost']:>8,.2f} ({item['percentage']:5.1f}%) {bar}")
            
        # Search by tag
        print("\n🔍 Search Resources by Tag...")
        
        prod_resources = platform.tag_manager.get_resources_by_tag("Environment", "production")
        print(f"\n  Environment=production: {len(prod_resources)} resources")
        for r in prod_resources[:5]:
            print(f"    • {r.name} ({r.resource_type.value})")
            
        platform_team = platform.tag_manager.get_resources_by_tag("Team", "platform")
        print(f"\n  Team=platform: {len(platform_team)} resources")
        for r in platform_team:
            print(f"    • {r.name} ({r.resource_type.value})")
            
        # Tag coverage
        print("\n📊 Tag Coverage Analysis:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Coverage by Tag:")
        total = stats["total_resources"]
        for tag, count in sorted(stats["tag_coverage"].items(), key=lambda x: x[1], reverse=True):
            percentage = count / total * 100
            bar = "█" * int(percentage / 5)
            print(f"    {tag:15}: {count:2}/{total} ({percentage:5.1f}%) {bar}")
            
        # Apply template to fix compliance
        print("\n🔧 Fixing Compliance Issues...")
        
        # Find non-compliant resources
        non_compliant = [r for r in platform.tag_manager.resources.values()
                         if r.compliance_status == ComplianceLevel.NON_COMPLIANT]
                         
        # Add missing CostCenter tags
        for resource in non_compliant:
            if "CostCenter" not in resource.tags:
                platform.tag_manager.add_tag(
                    resource.resource_id,
                    "CostCenter",
                    "IT001",
                    "auto-remediation"
                )
                
        # Re-run compliance
        report2 = platform.policy_engine.evaluate_all()
        
        print(f"\n  Before: {report.compliance_percentage:.1f}% compliant")
        print(f"  After:  {report2.compliance_percentage:.1f}% compliant")
        print(f"  Improved by: {report2.compliance_percentage - report.compliance_percentage:.1f}%")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Resources: {stats['total_resources']}")
        print(f"  Total Tags: {stats['total_tags']}")
        print(f"  Avg Tags/Resource: {stats['avg_tags_per_resource']:.1f}")
        print(f"  Compliance Rate: {stats['compliance_rate']:.1f}%")
        print(f"  Policies: {stats['policies']}")
        print(f"  Templates: {stats['templates']}")
        print(f"  Inheritance Rules: {stats['inheritance_rules']}")
        
        # Dashboard
        print("\n📋 Resource Tagging Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                Resource Tagging Overview                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Resources:       {stats['total_resources']:>10}                    │")
        print(f"  │ Total Tags:            {stats['total_tags']:>10}                    │")
        print(f"  │ Avg Tags/Resource:     {stats['avg_tags_per_resource']:>10.1f}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Compliance Rate:       {stats['compliance_rate']:>10.1f}%                   │")
        print(f"  │ Policies:              {stats['policies']:>10}                    │")
        print(f"  │ Templates:             {stats['templates']:>10}                    │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Resource Tagging Platform initialized!")
    print("=" * 60)
