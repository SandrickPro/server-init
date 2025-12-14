#!/usr/bin/env python3
"""
Server Init - Iteration 243: Access Control Platform
Платформа контроля доступа

Функционал:
- RBAC - ролевой контроль доступа
- ABAC - атрибутивный контроль доступа
- Policy Management - управление политиками
- Permission Sets - наборы разрешений
- Resource Hierarchy - иерархия ресурсов
- Access Audit - аудит доступа
- Policy Evaluation - вычисление политик
- Access Requests - запросы на доступ
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class PermissionEffect(Enum):
    """Эффект разрешения"""
    ALLOW = "allow"
    DENY = "deny"


class PolicyType(Enum):
    """Тип политики"""
    IDENTITY = "identity"
    RESOURCE = "resource"
    GROUP = "group"
    SERVICE = "service"


class ActionType(Enum):
    """Тип действия"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    ALL = "*"


class ResourceType(Enum):
    """Тип ресурса"""
    SERVICE = "service"
    DATABASE = "database"
    STORAGE = "storage"
    COMPUTE = "compute"
    NETWORK = "network"
    SECRET = "secret"


class RequestStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class Permission:
    """Разрешение"""
    permission_id: str
    name: str = ""
    
    # Resource
    resource_type: ResourceType = ResourceType.SERVICE
    resource_pattern: str = "*"
    
    # Actions
    actions: List[ActionType] = field(default_factory=list)
    
    # Effect
    effect: PermissionEffect = PermissionEffect.ALLOW
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Description
    description: str = ""


@dataclass
class Role:
    """Роль"""
    role_id: str
    name: str = ""
    
    # Permissions
    permissions: List[Permission] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    is_system: bool = False
    
    # Hierarchy
    parent_role: str = ""
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Principal:
    """Субъект доступа"""
    principal_id: str
    principal_type: str = "user"  # user, service, group
    name: str = ""
    
    # Roles
    roles: List[str] = field(default_factory=list)
    
    # Direct permissions
    direct_permissions: List[Permission] = field(default_factory=list)
    
    # Attributes (for ABAC)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Groups
    groups: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True


@dataclass
class Resource:
    """Ресурс"""
    resource_id: str
    resource_type: ResourceType = ResourceType.SERVICE
    name: str = ""
    
    # Path
    path: str = ""
    
    # Parent
    parent_id: str = ""
    
    # Owner
    owner_id: str = ""
    
    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Tags
    tags: List[str] = field(default_factory=list)


@dataclass
class Policy:
    """Политика доступа"""
    policy_id: str
    name: str = ""
    
    # Type
    policy_type: PolicyType = PolicyType.IDENTITY
    
    # Statements
    statements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Attached to
    attached_to: List[str] = field(default_factory=list)
    
    # Priority
    priority: int = 0
    
    # Status
    is_active: bool = True
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessDecision:
    """Решение о доступе"""
    decision_id: str
    
    # Request
    principal_id: str = ""
    resource_id: str = ""
    action: ActionType = ActionType.READ
    
    # Result
    allowed: bool = False
    effect: PermissionEffect = PermissionEffect.DENY
    
    # Matching
    matching_policies: List[str] = field(default_factory=list)
    
    # Reason
    reason: str = ""
    
    # Time
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessRequest:
    """Запрос на доступ"""
    request_id: str
    
    # Requester
    requester_id: str = ""
    
    # Target
    role_id: str = ""
    resource_id: str = ""
    
    # Details
    reason: str = ""
    duration_hours: int = 0  # 0 = permanent
    
    # Status
    status: RequestStatus = RequestStatus.PENDING
    
    # Approvals
    approvers: List[str] = field(default_factory=list)
    approved_by: str = ""
    
    # Time
    requested_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class AuditEntry:
    """Запись аудита"""
    audit_id: str
    
    # Who
    principal_id: str = ""
    principal_name: str = ""
    
    # What
    action: str = ""
    resource_id: str = ""
    resource_name: str = ""
    
    # Result
    allowed: bool = False
    
    # Context
    ip_address: str = ""
    user_agent: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


class AccessControlPlatform:
    """Платформа контроля доступа"""
    
    def __init__(self):
        self.principals: Dict[str, Principal] = {}
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, Resource] = {}
        self.policies: Dict[str, Policy] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.audit_log: List[AuditEntry] = []
        
        self._init_system_roles()
        
    def _init_system_roles(self):
        """Инициализация системных ролей"""
        admin_role = Role(
            role_id="role_admin",
            name="Administrator",
            description="Full system access",
            is_system=True,
            permissions=[
                Permission(
                    permission_id="perm_admin_all",
                    name="Admin All",
                    resource_pattern="*",
                    actions=[ActionType.ALL],
                    effect=PermissionEffect.ALLOW
                )
            ]
        )
        
        viewer_role = Role(
            role_id="role_viewer",
            name="Viewer",
            description="Read-only access",
            is_system=True,
            permissions=[
                Permission(
                    permission_id="perm_view_all",
                    name="View All",
                    resource_pattern="*",
                    actions=[ActionType.READ],
                    effect=PermissionEffect.ALLOW
                )
            ]
        )
        
        self.roles = {
            admin_role.role_id: admin_role,
            viewer_role.role_id: viewer_role
        }
        
    def create_role(self, name: str, permissions: List[Permission] = None,
                   description: str = "", parent_role: str = "") -> Role:
        """Создание роли"""
        role = Role(
            role_id=f"role_{uuid.uuid4().hex[:8]}",
            name=name,
            permissions=permissions or [],
            description=description,
            parent_role=parent_role
        )
        
        self.roles[role.role_id] = role
        return role
        
    def create_principal(self, name: str, principal_type: str = "user",
                        attributes: Dict[str, Any] = None) -> Principal:
        """Создание субъекта"""
        principal = Principal(
            principal_id=f"prin_{uuid.uuid4().hex[:8]}",
            principal_type=principal_type,
            name=name,
            attributes=attributes or {}
        )
        
        self.principals[principal.principal_id] = principal
        return principal
        
    def create_resource(self, name: str, resource_type: ResourceType,
                       path: str = "", owner_id: str = "",
                       attributes: Dict[str, Any] = None) -> Resource:
        """Создание ресурса"""
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            resource_type=resource_type,
            name=name,
            path=path or f"/{resource_type.value}/{name}",
            owner_id=owner_id,
            attributes=attributes or {}
        )
        
        self.resources[resource.resource_id] = resource
        return resource
        
    def assign_role(self, principal_id: str, role_id: str) -> bool:
        """Назначение роли"""
        principal = self.principals.get(principal_id)
        role = self.roles.get(role_id)
        
        if not principal or not role:
            return False
            
        if role_id not in principal.roles:
            principal.roles.append(role_id)
            
        return True
        
    def create_policy(self, name: str, statements: List[Dict[str, Any]],
                     policy_type: PolicyType = PolicyType.IDENTITY,
                     priority: int = 0) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_type=policy_type,
            statements=statements,
            priority=priority
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    def attach_policy(self, policy_id: str, target_id: str) -> bool:
        """Прикрепление политики"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False
            
        if target_id not in policy.attached_to:
            policy.attached_to.append(target_id)
            
        return True
        
    def evaluate_access(self, principal_id: str, resource_id: str,
                       action: ActionType) -> AccessDecision:
        """Оценка доступа"""
        decision = AccessDecision(
            decision_id=f"dec_{uuid.uuid4().hex[:8]}",
            principal_id=principal_id,
            resource_id=resource_id,
            action=action
        )
        
        principal = self.principals.get(principal_id)
        resource = self.resources.get(resource_id)
        
        if not principal:
            decision.reason = "Principal not found"
            self._audit_access(decision, principal, resource)
            return decision
            
        if not principal.is_active:
            decision.reason = "Principal is inactive"
            self._audit_access(decision, principal, resource)
            return decision
            
        # Collect all permissions
        all_permissions = []
        
        # Direct permissions
        all_permissions.extend(principal.direct_permissions)
        
        # Role permissions
        for role_id in principal.roles:
            role = self.roles.get(role_id)
            if role:
                all_permissions.extend(role.permissions)
                
                # Check parent roles
                parent_id = role.parent_role
                while parent_id:
                    parent = self.roles.get(parent_id)
                    if parent:
                        all_permissions.extend(parent.permissions)
                        parent_id = parent.parent_role
                    else:
                        break
                        
        # Policy permissions
        for policy in self.policies.values():
            if not policy.is_active:
                continue
                
            if principal_id in policy.attached_to:
                for stmt in policy.statements:
                    effect = PermissionEffect(stmt.get("effect", "deny"))
                    actions = stmt.get("actions", [])
                    resources = stmt.get("resources", [])
                    
                    perm = Permission(
                        permission_id=f"stmt_{policy.policy_id}",
                        resource_pattern=resources[0] if resources else "*",
                        actions=[ActionType(a) for a in actions],
                        effect=effect
                    )
                    all_permissions.append(perm)
                    
        # Evaluate permissions (deny takes precedence)
        allow_found = False
        deny_found = False
        
        for perm in all_permissions:
            if self._matches_resource(perm, resource) and self._matches_action(perm, action):
                decision.matching_policies.append(perm.permission_id)
                
                if perm.effect == PermissionEffect.DENY:
                    deny_found = True
                    break
                elif perm.effect == PermissionEffect.ALLOW:
                    allow_found = True
                    
        if deny_found:
            decision.allowed = False
            decision.effect = PermissionEffect.DENY
            decision.reason = "Explicit deny"
        elif allow_found:
            decision.allowed = True
            decision.effect = PermissionEffect.ALLOW
            decision.reason = "Permission granted"
        else:
            decision.allowed = False
            decision.effect = PermissionEffect.DENY
            decision.reason = "No matching permission"
            
        self._audit_access(decision, principal, resource)
        return decision
        
    def _matches_resource(self, permission: Permission, 
                         resource: Optional[Resource]) -> bool:
        """Проверка соответствия ресурса"""
        if permission.resource_pattern == "*":
            return True
            
        if not resource:
            return False
            
        pattern = permission.resource_pattern
        
        # Simple pattern matching
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return resource.path.startswith(prefix)
            
        return resource.path == pattern or resource.name == pattern
        
    def _matches_action(self, permission: Permission, action: ActionType) -> bool:
        """Проверка соответствия действия"""
        if ActionType.ALL in permission.actions:
            return True
            
        return action in permission.actions
        
    def _audit_access(self, decision: AccessDecision,
                     principal: Optional[Principal],
                     resource: Optional[Resource]):
        """Аудит доступа"""
        entry = AuditEntry(
            audit_id=f"aud_{uuid.uuid4().hex[:8]}",
            principal_id=decision.principal_id,
            principal_name=principal.name if principal else "",
            action=decision.action.value,
            resource_id=decision.resource_id,
            resource_name=resource.name if resource else "",
            allowed=decision.allowed
        )
        
        self.audit_log.append(entry)
        
    def request_access(self, requester_id: str, role_id: str = "",
                      resource_id: str = "", reason: str = "",
                      duration_hours: int = 0) -> AccessRequest:
        """Запрос на доступ"""
        request = AccessRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            requester_id=requester_id,
            role_id=role_id,
            resource_id=resource_id,
            reason=reason,
            duration_hours=duration_hours
        )
        
        self.access_requests[request.request_id] = request
        return request
        
    def approve_request(self, request_id: str, approver_id: str) -> bool:
        """Одобрение запроса"""
        request = self.access_requests.get(request_id)
        if not request or request.status != RequestStatus.PENDING:
            return False
            
        request.status = RequestStatus.APPROVED
        request.approved_by = approver_id
        request.resolved_at = datetime.now()
        
        if request.duration_hours > 0:
            request.expires_at = datetime.now() + timedelta(hours=request.duration_hours)
            
        # Grant access
        if request.role_id:
            self.assign_role(request.requester_id, request.role_id)
            
        return True
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        # Access decisions
        allowed = sum(1 for e in self.audit_log if e.allowed)
        denied = len(self.audit_log) - allowed
        
        # Requests
        pending = sum(1 for r in self.access_requests.values() 
                     if r.status == RequestStatus.PENDING)
        approved = sum(1 for r in self.access_requests.values() 
                      if r.status == RequestStatus.APPROVED)
                      
        return {
            "total_principals": len(self.principals),
            "total_roles": len(self.roles),
            "total_resources": len(self.resources),
            "total_policies": len(self.policies),
            "audit_entries": len(self.audit_log),
            "access_allowed": allowed,
            "access_denied": denied,
            "pending_requests": pending,
            "approved_requests": approved
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 243: Access Control Platform")
    print("=" * 60)
    
    platform = AccessControlPlatform()
    print("✓ Access Control Platform created")
    
    # Create principals
    print("\n👤 Creating Principals...")
    
    principals_data = [
        ("Alice Admin", "user", {"department": "IT", "level": "senior"}),
        ("Bob Developer", "user", {"department": "Engineering", "level": "junior"}),
        ("Carol Manager", "user", {"department": "Engineering", "level": "manager"}),
        ("api-service", "service", {"environment": "production"}),
        ("batch-processor", "service", {"environment": "production"}),
    ]
    
    principals = []
    for name, ptype, attrs in principals_data:
        p = platform.create_principal(name, ptype, attrs)
        principals.append(p)
        print(f"  👤 {name} ({ptype})")
        
    # Create roles
    print("\n🎭 Creating Roles...")
    
    developer_role = platform.create_role(
        "Developer",
        permissions=[
            Permission(
                permission_id="perm_dev_read",
                name="Dev Read",
                resource_type=ResourceType.SERVICE,
                resource_pattern="/service/*",
                actions=[ActionType.READ],
                effect=PermissionEffect.ALLOW
            ),
            Permission(
                permission_id="perm_dev_write",
                name="Dev Write",
                resource_type=ResourceType.SERVICE,
                resource_pattern="/service/dev-*",
                actions=[ActionType.WRITE],
                effect=PermissionEffect.ALLOW
            )
        ],
        description="Developer role"
    )
    print(f"  🎭 {developer_role.name}")
    
    dba_role = platform.create_role(
        "DBA",
        permissions=[
            Permission(
                permission_id="perm_dba_all",
                name="DBA Full",
                resource_type=ResourceType.DATABASE,
                resource_pattern="/database/*",
                actions=[ActionType.READ, ActionType.WRITE, ActionType.DELETE],
                effect=PermissionEffect.ALLOW
            )
        ],
        description="Database Administrator"
    )
    print(f"  🎭 {dba_role.name}")
    
    # Create resources
    print("\n📦 Creating Resources...")
    
    resources_data = [
        ("api-gateway", ResourceType.SERVICE, "/service/api-gateway"),
        ("user-service", ResourceType.SERVICE, "/service/user-service"),
        ("dev-test-service", ResourceType.SERVICE, "/service/dev-test-service"),
        ("users-db", ResourceType.DATABASE, "/database/users-db"),
        ("orders-db", ResourceType.DATABASE, "/database/orders-db"),
        ("app-secrets", ResourceType.SECRET, "/secret/app-secrets"),
    ]
    
    resources = []
    for name, rtype, path in resources_data:
        r = platform.create_resource(name, rtype, path, principals[0].principal_id)
        resources.append(r)
        print(f"  📦 {name} ({rtype.value})")
        
    # Assign roles
    print("\n🔗 Assigning Roles...")
    
    platform.assign_role(principals[0].principal_id, "role_admin")
    print(f"  ✓ {principals[0].name} → Administrator")
    
    platform.assign_role(principals[1].principal_id, developer_role.role_id)
    print(f"  ✓ {principals[1].name} → Developer")
    
    platform.assign_role(principals[2].principal_id, "role_viewer")
    print(f"  ✓ {principals[2].name} → Viewer")
    
    # Create policy
    print("\n📋 Creating Policies...")
    
    deny_secrets_policy = platform.create_policy(
        "Deny Secrets Access",
        statements=[{
            "effect": "deny",
            "actions": ["read", "write"],
            "resources": ["/secret/*"]
        }],
        policy_type=PolicyType.RESOURCE,
        priority=100
    )
    platform.attach_policy(deny_secrets_policy.policy_id, principals[1].principal_id)
    print(f"  📋 {deny_secrets_policy.name} → {principals[1].name}")
    
    # Evaluate access
    print("\n🔍 Evaluating Access...")
    
    test_cases = [
        (principals[0], resources[0], ActionType.WRITE, "Admin writes to api-gateway"),
        (principals[1], resources[0], ActionType.READ, "Developer reads api-gateway"),
        (principals[1], resources[2], ActionType.WRITE, "Developer writes to dev-test-service"),
        (principals[1], resources[5], ActionType.READ, "Developer reads secrets"),
        (principals[2], resources[3], ActionType.READ, "Manager reads users-db"),
        (principals[2], resources[3], ActionType.WRITE, "Manager writes users-db"),
    ]
    
    decisions = []
    for principal, resource, action, desc in test_cases:
        decision = platform.evaluate_access(
            principal.principal_id,
            resource.resource_id,
            action
        )
        decisions.append(decision)
        
        icon = "✅" if decision.allowed else "❌"
        print(f"  {icon} {desc}: {decision.reason}")
        
    # Access requests
    print("\n📝 Creating Access Requests...")
    
    request = platform.request_access(
        principals[1].principal_id,
        role_id=dba_role.role_id,
        reason="Need database access for new feature",
        duration_hours=24
    )
    print(f"  📝 {principals[1].name} → DBA role (pending)")
    
    platform.approve_request(request.request_id, principals[0].principal_id)
    print(f"  ✓ Approved by {principals[0].name}")
    
    # Display roles
    print("\n📊 Role Summary:")
    
    print("\n  ┌─────────────────┬────────────────┬──────────────┬────────────┐")
    print("  │ Role            │ Permissions    │ Type         │ Status     │")
    print("  ├─────────────────┼────────────────┼──────────────┼────────────┤")
    
    for role_id, role in platform.roles.items():
        name = role.name[:15].ljust(15)
        perms = str(len(role.permissions))[:14].ljust(14)
        rtype = ("System" if role.is_system else "Custom")[:12].ljust(12)
        status = "🟢 Active"
        
        print(f"  │ {name} │ {perms} │ {rtype} │ {status:10s} │")
        
    print("  └─────────────────┴────────────────┴──────────────┴────────────┘")
    
    # Display principals
    print("\n👤 Principal Summary:")
    
    print("\n  ┌─────────────────────┬──────────────┬──────────────┬────────────┐")
    print("  │ Principal           │ Type         │ Roles        │ Status     │")
    print("  ├─────────────────────┼──────────────┼──────────────┼────────────┤")
    
    for principal in principals:
        name = principal.name[:19].ljust(19)
        ptype = principal.principal_type[:12].ljust(12)
        roles = str(len(principal.roles))[:12].ljust(12)
        status = "🟢" if principal.is_active else "🔴"
        
        print(f"  │ {name} │ {ptype} │ {roles} │ {status:10s} │")
        
    print("  └─────────────────────┴──────────────┴──────────────┴────────────┘")
    
    # Audit log
    print("\n📜 Recent Audit Log:")
    
    print("\n  ┌───────────────────┬───────────────────┬────────────┬─────────┐")
    print("  │ Principal         │ Resource          │ Action     │ Result  │")
    print("  ├───────────────────┼───────────────────┼────────────┼─────────┤")
    
    for entry in platform.audit_log[-8:]:
        principal = entry.principal_name[:17].ljust(17)
        resource = entry.resource_name[:17].ljust(17)
        action = entry.action[:10].ljust(10)
        result = "✅" if entry.allowed else "❌"
        
        print(f"  │ {principal} │ {resource} │ {action} │ {result:7s} │")
        
    print("  └───────────────────┴───────────────────┴────────────┴─────────┘")
    
    # Access matrix
    print("\n📊 Access Matrix:")
    
    print("\n  Resource         │", end="")
    for p in principals[:4]:
        print(f" {p.name[:8]:8s} │", end="")
    print()
    
    print("  ─────────────────┼" + "──────────┼" * 4)
    
    for resource in resources[:4]:
        print(f"  {resource.name[:15]:15s} │", end="")
        
        for principal in principals[:4]:
            dec = platform.evaluate_access(
                principal.principal_id,
                resource.resource_id,
                ActionType.READ
            )
            icon = "✅" if dec.allowed else "❌"
            print(f" {icon:8s} │", end="")
        print()
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Principals: {stats['total_principals']}")
    print(f"  Total Roles: {stats['total_roles']}")
    print(f"  Total Resources: {stats['total_resources']}")
    print(f"  Total Policies: {stats['total_policies']}")
    
    print(f"\n  Audit Entries: {stats['audit_entries']}")
    print(f"  Access Allowed: {stats['access_allowed']}")
    print(f"  Access Denied: {stats['access_denied']}")
    
    # Access rate
    if stats['audit_entries'] > 0:
        allow_rate = stats['access_allowed'] / stats['audit_entries'] * 100
        print(f"\n  Allow Rate: {allow_rate:.1f}%")
        
        bar_allow = int(allow_rate / 10)
        bar_deny = 10 - bar_allow
        print(f"  [{'█' * bar_allow}{'░' * bar_deny}]")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Access Control Dashboard                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Principals:                    {stats['total_principals']:>12}                        │")
    print(f"│ Roles:                         {stats['total_roles']:>12}                        │")
    print(f"│ Resources:                     {stats['total_resources']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Access Allowed:                {stats['access_allowed']:>12}                        │")
    print(f"│ Access Denied:                 {stats['access_denied']:>12}                        │")
    print(f"│ Pending Requests:              {stats['pending_requests']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Access Control Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
