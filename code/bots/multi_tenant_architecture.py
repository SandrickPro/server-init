#!/usr/bin/env python3
"""
Multi-Tenant Architecture Platform v13.0
Complete tenant isolation with RBAC, billing, and resource management
Enterprise SaaS-ready multi-tenancy
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import sqlite3
from pathlib import Path
import hashlib
import jwt
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
TENANT_DB = '/var/lib/tenants/multi_tenant.db'
JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

for directory in [os.path.dirname(TENANT_DB)]:
    Path(directory).mkdir(parents=True, exist_ok=True)

################################################################################
# Data Models
################################################################################

class TenantPlan(Enum):
    """Tenant subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class TenantStatus(Enum):
    """Tenant status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"

class Permission(Enum):
    """Fine-grained permissions"""
    # Resource permissions
    RESOURCE_READ = "resource:read"
    RESOURCE_WRITE = "resource:write"
    RESOURCE_DELETE = "resource:delete"
    
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    
    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    
    # Admin
    ADMIN_ALL = "admin:all"

class Role(Enum):
    """Predefined roles"""
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    BILLING = "billing"

@dataclass
class Tenant:
    """Tenant (organization)"""
    tenant_id: str
    name: str
    plan: TenantPlan
    status: TenantStatus
    domain: Optional[str] = None
    max_users: int = 5
    max_resources: int = 100
    features: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    trial_ends_at: Optional[datetime] = None

@dataclass
class User:
    """User within a tenant"""
    user_id: str
    tenant_id: str
    email: str
    name: str
    role: Role
    permissions: Set[Permission]
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

@dataclass
class ResourceQuota:
    """Resource quotas per tenant"""
    tenant_id: str
    cpu_cores: float
    memory_gb: float
    storage_gb: float
    bandwidth_gb: float
    api_requests_per_hour: int
    used_cpu: float = 0.0
    used_memory: float = 0.0
    used_storage: float = 0.0
    used_bandwidth: float = 0.0
    api_requests_count: int = 0

@dataclass
class BillingRecord:
    """Billing record"""
    record_id: str
    tenant_id: str
    period_start: datetime
    period_end: datetime
    amount: Decimal
    currency: str
    line_items: List[Dict[str, Any]]
    paid: bool = False
    paid_at: Optional[datetime] = None

################################################################################
# Database Manager
################################################################################

class TenantDatabase:
    """Multi-tenant database manager"""
    
    def __init__(self, db_path: str = TENANT_DB):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tenants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan TEXT NOT NULL,
                status TEXT NOT NULL,
                domain TEXT UNIQUE,
                max_users INTEGER DEFAULT 5,
                max_resources INTEGER DEFAULT 100,
                features_json TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trial_ends_at TIMESTAMP
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                permissions_json TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id),
                UNIQUE(tenant_id, email)
            )
        ''')
        
        # Resource quotas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_quotas (
                tenant_id TEXT PRIMARY KEY,
                cpu_cores REAL NOT NULL,
                memory_gb REAL NOT NULL,
                storage_gb REAL NOT NULL,
                bandwidth_gb REAL NOT NULL,
                api_requests_per_hour INTEGER NOT NULL,
                used_cpu REAL DEFAULT 0.0,
                used_memory REAL DEFAULT 0.0,
                used_storage REAL DEFAULT 0.0,
                used_bandwidth REAL DEFAULT 0.0,
                api_requests_count INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')
        
        # Tenant resources (isolated data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenant_resources (
                resource_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                resource_data_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')
        
        # Billing records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS billing_records (
                record_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                period_start TIMESTAMP NOT NULL,
                period_end TIMESTAMP NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                line_items_json TEXT NOT NULL,
                paid INTEGER DEFAULT 0,
                paid_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')
        
        # Audit log (tenant actions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                details_json TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # API keys per tenant
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                scopes_json TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')
        
        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_tenant ON tenant_resources(tenant_id, resource_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_billing_tenant ON billing_records(tenant_id, period_start)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_log(tenant_id, timestamp DESC)')
        
        self.conn.commit()
        logger.info(f"Multi-tenant database initialized: {db_path}")
    
    def create_tenant(self, tenant: Tenant) -> bool:
        """Create new tenant"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO tenants 
                (tenant_id, name, plan, status, domain, max_users, max_resources,
                 features_json, metadata_json, trial_ends_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tenant.tenant_id,
                tenant.name,
                tenant.plan.value,
                tenant.status.value,
                tenant.domain,
                tenant.max_users,
                tenant.max_resources,
                json.dumps(tenant.features),
                json.dumps(tenant.metadata),
                tenant.trial_ends_at.isoformat() if tenant.trial_ends_at else None
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Tenant creation failed: {e}")
            return False
    
    def create_user(self, user: User) -> bool:
        """Create user in tenant"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users 
                (user_id, tenant_id, email, name, role, permissions_json,
                 is_active, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id,
                user.tenant_id,
                user.email,
                user.name,
                user.role.value,
                json.dumps([p.value for p in user.permissions]),
                1 if user.is_active else 0,
                json.dumps(user.metadata)
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return False
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tenants WHERE tenant_id = ?', (tenant_id,))
        row = cursor.fetchone()
        
        if row:
            return Tenant(
                tenant_id=row[0],
                name=row[1],
                plan=TenantPlan(row[2]),
                status=TenantStatus(row[3]),
                domain=row[4],
                max_users=row[5],
                max_resources=row[6],
                features=json.loads(row[7]) if row[7] else {},
                metadata=json.loads(row[8]) if row[8] else {},
                created_at=datetime.fromisoformat(row[9]),
                trial_ends_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None
    
    def log_audit(self, tenant_id: str, user_id: str, action: str,
                 resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None,
                 details: Optional[Dict] = None,
                 ip_address: Optional[str] = None):
        """Log audit event"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO audit_log 
            (tenant_id, user_id, action, resource_type, resource_id,
             details_json, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            tenant_id,
            user_id,
            action,
            resource_type,
            resource_id,
            json.dumps(details) if details else None,
            ip_address
        ))
        self.conn.commit()

################################################################################
# RBAC Manager
################################################################################

class RBACManager:
    """Role-Based Access Control manager"""
    
    # Role to permissions mapping
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.OWNER: {
            Permission.ADMIN_ALL,
            Permission.RESOURCE_READ, Permission.RESOURCE_WRITE, Permission.RESOURCE_DELETE,
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
            Permission.BILLING_READ, Permission.BILLING_WRITE,
            Permission.SETTINGS_READ, Permission.SETTINGS_WRITE
        },
        Role.ADMIN: {
            Permission.RESOURCE_READ, Permission.RESOURCE_WRITE, Permission.RESOURCE_DELETE,
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
            Permission.SETTINGS_READ, Permission.SETTINGS_WRITE
        },
        Role.DEVELOPER: {
            Permission.RESOURCE_READ, Permission.RESOURCE_WRITE,
            Permission.USER_READ
        },
        Role.VIEWER: {
            Permission.RESOURCE_READ,
            Permission.USER_READ
        },
        Role.BILLING: {
            Permission.RESOURCE_READ,
            Permission.BILLING_READ, Permission.BILLING_WRITE
        }
    }
    
    @classmethod
    def get_role_permissions(cls, role: Role) -> Set[Permission]:
        """Get permissions for role"""
        return cls.ROLE_PERMISSIONS.get(role, set())
    
    @classmethod
    def has_permission(cls, user: User, permission: Permission) -> bool:
        """Check if user has permission"""
        return permission in user.permissions or Permission.ADMIN_ALL in user.permissions
    
    @classmethod
    def check_permission(cls, user: User, permission: Permission):
        """Check permission and raise if not allowed"""
        if not cls.has_permission(user, permission):
            raise PermissionError(f"User {user.user_id} lacks permission: {permission.value}")

################################################################################
# Resource Isolation Manager
################################################################################

class ResourceIsolationManager:
    """Manage tenant resource isolation"""
    
    def __init__(self, db: TenantDatabase):
        self.db = db
    
    def create_resource(self, tenant_id: str, resource_type: str,
                       resource_name: str, resource_data: Dict) -> str:
        """Create tenant-scoped resource"""
        resource_id = str(uuid.uuid4())
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT INTO tenant_resources 
            (resource_id, tenant_id, resource_type, resource_name, resource_data_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            resource_id,
            tenant_id,
            resource_type,
            resource_name,
            json.dumps(resource_data)
        ))
        self.db.conn.commit()
        
        return resource_id
    
    def get_tenant_resources(self, tenant_id: str, 
                           resource_type: Optional[str] = None) -> List[Dict]:
        """Get all resources for tenant"""
        cursor = self.db.conn.cursor()
        
        if resource_type:
            cursor.execute('''
                SELECT resource_id, resource_type, resource_name, resource_data_json
                FROM tenant_resources
                WHERE tenant_id = ? AND resource_type = ?
                ORDER BY created_at DESC
            ''', (tenant_id, resource_type))
        else:
            cursor.execute('''
                SELECT resource_id, resource_type, resource_name, resource_data_json
                FROM tenant_resources
                WHERE tenant_id = ?
                ORDER BY created_at DESC
            ''', (tenant_id,))
        
        resources = []
        for row in cursor.fetchall():
            resources.append({
                'resource_id': row[0],
                'resource_type': row[1],
                'resource_name': row[2],
                'resource_data': json.loads(row[3])
            })
        
        return resources
    
    def check_quota(self, tenant_id: str, resource_type: str) -> bool:
        """Check if tenant has quota available"""
        cursor = self.db.conn.cursor()
        
        # Get current count
        cursor.execute('''
            SELECT COUNT(*) FROM tenant_resources
            WHERE tenant_id = ? AND resource_type = ?
        ''', (tenant_id, resource_type))
        
        current_count = cursor.fetchone()[0]
        
        # Get max resources
        tenant = self.db.get_tenant(tenant_id)
        if tenant:
            return current_count < tenant.max_resources
        
        return False

################################################################################
# Billing Manager
################################################################################

class BillingManager:
    """Manage tenant billing"""
    
    # Pricing per plan (monthly, USD)
    PLAN_PRICING = {
        TenantPlan.FREE: Decimal('0.00'),
        TenantPlan.STARTER: Decimal('29.00'),
        TenantPlan.PROFESSIONAL: Decimal('99.00'),
        TenantPlan.ENTERPRISE: Decimal('499.00')
    }
    
    # Resource pricing (per unit)
    RESOURCE_PRICING = {
        'cpu_core': Decimal('10.00'),
        'memory_gb': Decimal('5.00'),
        'storage_gb': Decimal('0.10'),
        'bandwidth_gb': Decimal('0.05'),
        'api_request_1000': Decimal('0.01')
    }
    
    def __init__(self, db: TenantDatabase):
        self.db = db
    
    def calculate_bill(self, tenant_id: str, period_start: datetime,
                      period_end: datetime) -> BillingRecord:
        """Calculate bill for tenant"""
        tenant = self.db.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        line_items = []
        total = Decimal('0.00')
        
        # Base plan fee
        plan_fee = self.PLAN_PRICING[tenant.plan]
        line_items.append({
            'description': f'{tenant.plan.value.title()} Plan',
            'amount': float(plan_fee),
            'quantity': 1
        })
        total += plan_fee
        
        # Resource usage
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT used_cpu, used_memory, used_storage, used_bandwidth, api_requests_count
            FROM resource_quotas
            WHERE tenant_id = ?
        ''', (tenant_id,))
        
        row = cursor.fetchone()
        if row:
            used_cpu, used_memory, used_storage, used_bandwidth, api_requests = row
            
            # CPU usage
            if used_cpu > 0:
                cpu_cost = Decimal(str(used_cpu)) * self.RESOURCE_PRICING['cpu_core']
                line_items.append({
                    'description': 'CPU Hours',
                    'amount': float(cpu_cost),
                    'quantity': used_cpu
                })
                total += cpu_cost
            
            # Storage usage
            if used_storage > 0:
                storage_cost = Decimal(str(used_storage)) * self.RESOURCE_PRICING['storage_gb']
                line_items.append({
                    'description': 'Storage (GB)',
                    'amount': float(storage_cost),
                    'quantity': used_storage
                })
                total += storage_cost
        
        record = BillingRecord(
            record_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            amount=total,
            currency='USD',
            line_items=line_items
        )
        
        # Save to database
        cursor.execute('''
            INSERT INTO billing_records 
            (record_id, tenant_id, period_start, period_end, amount,
             currency, line_items_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.record_id,
            record.tenant_id,
            record.period_start.isoformat(),
            record.period_end.isoformat(),
            float(record.amount),
            record.currency,
            json.dumps(record.line_items)
        ))
        self.db.conn.commit()
        
        return record

################################################################################
# JWT Authentication
################################################################################

class JWTAuth:
    """JWT token generation and validation"""
    
    @staticmethod
    def generate_token(user: User, tenant: Tenant) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user.user_id,
            'tenant_id': tenant.tenant_id,
            'email': user.email,
            'role': user.role.value,
            'permissions': [p.value for p in user.permissions],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def validate_token(token: str) -> Dict:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

################################################################################
# Multi-Tenant Platform
################################################################################

class MultiTenantPlatform:
    """Main multi-tenant orchestrator"""
    
    def __init__(self):
        self.db = TenantDatabase()
        self.rbac = RBACManager()
        self.resource_manager = ResourceIsolationManager(self.db)
        self.billing = BillingManager(self.db)
    
    def create_tenant(self, name: str, owner_email: str, owner_name: str,
                     plan: TenantPlan = TenantPlan.FREE) -> tuple[Tenant, User, str]:
        """Create new tenant with owner"""
        
        # Create tenant
        tenant = Tenant(
            tenant_id=str(uuid.uuid4()),
            name=name,
            plan=plan,
            status=TenantStatus.TRIAL if plan != TenantPlan.FREE else TenantStatus.ACTIVE,
            trial_ends_at=datetime.now() + timedelta(days=14) if plan != TenantPlan.FREE else None
        )
        
        if not self.db.create_tenant(tenant):
            raise ValueError("Failed to create tenant")
        
        # Create owner user
        owner = User(
            user_id=str(uuid.uuid4()),
            tenant_id=tenant.tenant_id,
            email=owner_email,
            name=owner_name,
            role=Role.OWNER,
            permissions=self.rbac.get_role_permissions(Role.OWNER)
        )
        
        if not self.db.create_user(owner):
            raise ValueError("Failed to create owner")
        
        # Generate JWT token
        token = JWTAuth.generate_token(owner, tenant)
        
        logger.info(f"Tenant created: {tenant.name} ({tenant.tenant_id})")
        
        return tenant, owner, token
    
    def add_user_to_tenant(self, tenant_id: str, email: str, name: str,
                          role: Role, requester: User) -> User:
        """Add user to tenant (with permission check)"""
        
        # Check permission
        self.rbac.check_permission(requester, Permission.USER_CREATE)
        
        # Create user
        user = User(
            user_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role,
            permissions=self.rbac.get_role_permissions(role)
        )
        
        if not self.db.create_user(user):
            raise ValueError("Failed to create user")
        
        # Audit log
        self.db.log_audit(
            tenant_id,
            requester.user_id,
            'user_created',
            resource_type='user',
            resource_id=user.user_id,
            details={'email': email, 'role': role.value}
        )
        
        return user

################################################################################
# CLI Interface
################################################################################

def main():
    """Main entry point"""
    logger.info("Multi-Tenant Architecture Platform v13.0")
    
    if '--create-tenant' in sys.argv:
        platform = MultiTenantPlatform()
        
        tenant, owner, token = platform.create_tenant(
            name="Example Corp",
            owner_email="owner@example.com",
            owner_name="John Doe",
            plan=TenantPlan.PROFESSIONAL
        )
        
        print(f"""
✅ Tenant Created
-----------------
Tenant ID: {tenant.tenant_id}
Name: {tenant.name}
Plan: {tenant.plan.value}
Owner: {owner.name} ({owner.email})

JWT Token:
{token}
        """)
    
    elif '--test-rbac' in sys.argv:
        # Test RBAC
        tenant = Tenant(
            tenant_id=str(uuid.uuid4()),
            name="Test Corp",
            plan=TenantPlan.STARTER,
            status=TenantStatus.ACTIVE
        )
        
        owner = User(
            user_id=str(uuid.uuid4()),
            tenant_id=tenant.tenant_id,
            email="owner@test.com",
            name="Owner",
            role=Role.OWNER,
            permissions=RBACManager.get_role_permissions(Role.OWNER)
        )
        
        print(f"Owner permissions: {len(owner.permissions)}")
        print(f"Can delete resources: {RBACManager.has_permission(owner, Permission.RESOURCE_DELETE)}")
    
    else:
        print("""
Multi-Tenant Architecture Platform v13.0

Usage:
  --create-tenant    Create new tenant
  --test-rbac        Test RBAC system

Examples:
  python3 multi_tenant_architecture.py --create-tenant
        """)

if __name__ == '__main__':
    main()
