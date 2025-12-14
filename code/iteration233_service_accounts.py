#!/usr/bin/env python3
"""
Server Init - Iteration 233: Service Accounts Platform
Платформа сервисных аккаунтов

Функционал:
- Service Account Management - управление сервисными аккаунтами
- Token Generation - генерация токенов
- Token Rotation - ротация токенов
- Permission Management - управление разрешениями
- Audit Logging - логирование действий
- Secret Storage - хранение секретов
- API Key Management - управление API ключами
- Expiration Policies - политики истечения
"""

import asyncio
import random
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class AccountType(Enum):
    """Тип аккаунта"""
    SERVICE = "service"
    BOT = "bot"
    CI_CD = "ci_cd"
    EXTERNAL = "external"


class AccountStatus(Enum):
    """Статус аккаунта"""
    ACTIVE = "active"
    DISABLED = "disabled"
    SUSPENDED = "suspended"
    PENDING = "pending"


class TokenType(Enum):
    """Тип токена"""
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"
    JWT = "jwt"


class TokenStatus(Enum):
    """Статус токена"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    ROTATED = "rotated"


class PermissionScope(Enum):
    """Область разрешений"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class Permission:
    """Разрешение"""
    permission_id: str
    resource: str = ""
    scope: PermissionScope = PermissionScope.READ
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PermissionSet:
    """Набор разрешений"""
    set_id: str
    name: str = ""
    description: str = ""
    
    # Permissions
    permissions: List[Permission] = field(default_factory=list)
    
    # Predefined
    is_predefined: bool = False


@dataclass
class Token:
    """Токен"""
    token_id: str
    account_id: str = ""
    
    # Type
    token_type: TokenType = TokenType.ACCESS
    
    # Value (hashed)
    token_hash: str = ""
    token_prefix: str = ""  # First 8 chars for identification
    
    # Status
    status: TokenStatus = TokenStatus.ACTIVE
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    # Metadata
    name: str = ""
    description: str = ""
    
    # IP restrictions
    allowed_ips: List[str] = field(default_factory=list)
    
    # Usage
    usage_count: int = 0


@dataclass
class ServiceAccount:
    """Сервисный аккаунт"""
    account_id: str
    name: str = ""
    description: str = ""
    
    # Type
    account_type: AccountType = AccountType.SERVICE
    
    # Status
    status: AccountStatus = AccountStatus.ACTIVE
    
    # Owner
    owner: str = ""
    owner_email: str = ""
    
    # Project/namespace
    project: str = ""
    namespace: str = ""
    
    # Permissions
    permission_sets: List[str] = field(default_factory=list)
    
    # Tokens
    active_tokens: int = 0
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    account_id: str = ""
    
    # Name
    name: str = ""
    
    # Value (encrypted)
    encrypted_value: str = ""
    
    # Version
    version: int = 1
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    
    # Account
    account_id: str = ""
    
    # Action
    action: str = ""
    resource: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Source
    source_ip: str = ""
    user_agent: str = ""
    
    # Result
    success: bool = True
    error: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RotationPolicy:
    """Политика ротации"""
    policy_id: str
    name: str = ""
    
    # Schedule
    rotation_days: int = 30
    
    # Warning
    warning_days: int = 7
    
    # Auto-rotate
    auto_rotate: bool = True
    
    # Overlap period (hours)
    overlap_hours: int = 24


class TokenGenerator:
    """Генератор токенов"""
    
    @staticmethod
    def generate_token(token_type: TokenType) -> str:
        """Генерация токена"""
        if token_type == TokenType.API_KEY:
            prefix = "sk_live_"
            token = prefix + secrets.token_urlsafe(32)
        elif token_type == TokenType.JWT:
            # Simplified JWT-like token
            header = secrets.token_urlsafe(10)
            payload = secrets.token_urlsafe(20)
            signature = secrets.token_urlsafe(15)
            token = f"{header}.{payload}.{signature}"
        else:
            token = secrets.token_urlsafe(48)
        return token
        
    @staticmethod
    def hash_token(token: str) -> str:
        """Хеширование токена"""
        return hashlib.sha256(token.encode()).hexdigest()


class ServiceAccountManager:
    """Менеджер сервисных аккаунтов"""
    
    def __init__(self):
        self.accounts: Dict[str, ServiceAccount] = {}
        self.tokens: Dict[str, Token] = {}
        self.secrets: Dict[str, Secret] = {}
        self.permission_sets: Dict[str, PermissionSet] = {}
        self.rotation_policies: Dict[str, RotationPolicy] = {}
        self.audit_log: List[AuditEntry] = []
        self.generator = TokenGenerator()
        
        self._init_permission_sets()
        
    def _init_permission_sets(self):
        """Инициализация стандартных наборов разрешений"""
        # Read-only
        readonly = PermissionSet(
            set_id="pset_readonly",
            name="ReadOnly",
            description="Read-only access",
            permissions=[
                Permission(
                    permission_id="perm_read_all",
                    resource="*",
                    scope=PermissionScope.READ
                )
            ],
            is_predefined=True
        )
        
        # CI/CD
        cicd = PermissionSet(
            set_id="pset_cicd",
            name="CI/CD",
            description="CI/CD pipeline access",
            permissions=[
                Permission(
                    permission_id="perm_deploy",
                    resource="deployments/*",
                    scope=PermissionScope.WRITE
                ),
                Permission(
                    permission_id="perm_registry",
                    resource="registry/*",
                    scope=PermissionScope.WRITE
                )
            ],
            is_predefined=True
        )
        
        # Admin
        admin = PermissionSet(
            set_id="pset_admin",
            name="Admin",
            description="Full administrative access",
            permissions=[
                Permission(
                    permission_id="perm_admin_all",
                    resource="*",
                    scope=PermissionScope.ADMIN
                )
            ],
            is_predefined=True
        )
        
        self.permission_sets = {
            readonly.set_id: readonly,
            cicd.set_id: cicd,
            admin.set_id: admin
        }
        
    def create_account(self, name: str, account_type: AccountType,
                      owner: str, project: str = "",
                      permission_sets: List[str] = None) -> ServiceAccount:
        """Создание сервисного аккаунта"""
        account = ServiceAccount(
            account_id=f"sa_{uuid.uuid4().hex[:12]}",
            name=name,
            account_type=account_type,
            owner=owner,
            project=project,
            permission_sets=permission_sets or []
        )
        
        self.accounts[account.account_id] = account
        self._audit("create_account", account.account_id, {"name": name})
        
        return account
        
    def create_token(self, account_id: str, name: str,
                    token_type: TokenType = TokenType.ACCESS,
                    expires_days: int = 90) -> tuple[Token, str]:
        """Создание токена (возвращает токен и его значение)"""
        account = self.accounts.get(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")
            
        # Generate token
        raw_token = self.generator.generate_token(token_type)
        
        token = Token(
            token_id=f"tok_{uuid.uuid4().hex[:8]}",
            account_id=account_id,
            token_type=token_type,
            token_hash=self.generator.hash_token(raw_token),
            token_prefix=raw_token[:8],
            name=name,
            expires_at=datetime.now() + timedelta(days=expires_days)
        )
        
        self.tokens[token.token_id] = token
        account.active_tokens += 1
        
        self._audit("create_token", account_id, {
            "token_id": token.token_id,
            "name": name
        })
        
        return token, raw_token
        
    def rotate_token(self, token_id: str) -> tuple[Optional[Token], Optional[str]]:
        """Ротация токена"""
        old_token = self.tokens.get(token_id)
        if not old_token:
            return None, None
            
        # Mark old token as rotated
        old_token.status = TokenStatus.ROTATED
        
        # Create new token
        new_token, raw_token = self.create_token(
            old_token.account_id,
            f"{old_token.name} (rotated)",
            old_token.token_type
        )
        
        self._audit("rotate_token", old_token.account_id, {
            "old_token": token_id,
            "new_token": new_token.token_id
        })
        
        return new_token, raw_token
        
    def revoke_token(self, token_id: str):
        """Отзыв токена"""
        token = self.tokens.get(token_id)
        if not token:
            return
            
        token.status = TokenStatus.REVOKED
        
        account = self.accounts.get(token.account_id)
        if account:
            account.active_tokens = max(0, account.active_tokens - 1)
            
        self._audit("revoke_token", token.account_id, {"token_id": token_id})
        
    def validate_token(self, raw_token: str) -> Optional[ServiceAccount]:
        """Валидация токена"""
        token_hash = self.generator.hash_token(raw_token)
        
        for token in self.tokens.values():
            if token.token_hash == token_hash:
                # Check status
                if token.status != TokenStatus.ACTIVE:
                    return None
                    
                # Check expiration
                if token.expires_at and datetime.now() > token.expires_at:
                    token.status = TokenStatus.EXPIRED
                    return None
                    
                # Update usage
                token.usage_count += 1
                token.last_used = datetime.now()
                
                # Get account
                account = self.accounts.get(token.account_id)
                if account:
                    account.last_activity = datetime.now()
                    
                return account
                
        return None
        
    def store_secret(self, account_id: str, name: str, value: str) -> Secret:
        """Сохранение секрета"""
        # Simple "encryption" (in real system would use proper encryption)
        encrypted = hashlib.sha256(value.encode()).hexdigest()
        
        secret = Secret(
            secret_id=f"sec_{uuid.uuid4().hex[:8]}",
            account_id=account_id,
            name=name,
            encrypted_value=encrypted
        )
        
        self.secrets[secret.secret_id] = secret
        self._audit("store_secret", account_id, {"name": name})
        
        return secret
        
    def _audit(self, action: str, account_id: str, details: Dict[str, Any]):
        """Добавление записи аудита"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            account_id=account_id,
            action=action,
            details=details,
            source_ip=f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
        )
        self.audit_log.append(entry)
        
    def get_expiring_tokens(self, days: int = 7) -> List[Token]:
        """Получение истекающих токенов"""
        threshold = datetime.now() + timedelta(days=days)
        
        expiring = []
        for token in self.tokens.values():
            if token.status == TokenStatus.ACTIVE and token.expires_at:
                if token.expires_at < threshold:
                    expiring.append(token)
                    
        return expiring
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        accounts = list(self.accounts.values())
        tokens = list(self.tokens.values())
        
        active_accounts = [a for a in accounts if a.status == AccountStatus.ACTIVE]
        active_tokens = [t for t in tokens if t.status == TokenStatus.ACTIVE]
        
        # By type
        by_type = {}
        for acc in accounts:
            t = acc.account_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        return {
            "total_accounts": len(accounts),
            "active_accounts": len(active_accounts),
            "total_tokens": len(tokens),
            "active_tokens": len(active_tokens),
            "secrets": len(self.secrets),
            "audit_entries": len(self.audit_log),
            "accounts_by_type": by_type
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 233: Service Accounts Platform")
    print("=" * 60)
    
    manager = ServiceAccountManager()
    print("✓ Service Accounts Platform created")
    
    # Create service accounts
    print("\n👤 Creating Service Accounts...")
    
    accounts_config = [
        ("ci-pipeline", AccountType.CI_CD, "devops-team", "platform"),
        ("monitoring-agent", AccountType.SERVICE, "sre-team", "monitoring"),
        ("backup-service", AccountType.SERVICE, "ops-team", "backup"),
        ("github-bot", AccountType.BOT, "devops-team", "integration"),
        ("slack-bot", AccountType.BOT, "platform-team", "integration"),
        ("external-api", AccountType.EXTERNAL, "partner-team", "api"),
        ("deployment-bot", AccountType.CI_CD, "devops-team", "platform"),
        ("data-sync", AccountType.SERVICE, "data-team", "etl"),
    ]
    
    accounts = []
    for name, acc_type, owner, project in accounts_config:
        perm_sets = ["pset_readonly"]
        if acc_type == AccountType.CI_CD:
            perm_sets = ["pset_cicd"]
        elif acc_type == AccountType.SERVICE:
            perm_sets = ["pset_readonly"]
            
        account = manager.create_account(name, acc_type, owner, project, perm_sets)
        accounts.append(account)
        
        type_icons = {
            AccountType.SERVICE: "🔧",
            AccountType.BOT: "🤖",
            AccountType.CI_CD: "⚙️",
            AccountType.EXTERNAL: "🌐"
        }
        icon = type_icons.get(acc_type, "📋")
        print(f"  {icon} {name} ({acc_type.value}) - {project}")
        
    # Create tokens for accounts
    print("\n🔑 Generating Tokens...")
    
    created_tokens = []
    raw_tokens = {}
    
    for account in accounts:
        # Create 1-2 tokens per account
        num_tokens = random.randint(1, 2)
        for i in range(num_tokens):
            token_type = random.choice([TokenType.ACCESS, TokenType.API_KEY])
            token, raw = manager.create_token(
                account.account_id,
                f"{account.name}-token-{i+1}",
                token_type,
                expires_days=random.randint(30, 180)
            )
            created_tokens.append(token)
            raw_tokens[token.token_id] = raw
            
    print(f"  ✓ Created {len(created_tokens)} tokens")
    
    # Store some secrets
    print("\n🔐 Storing Secrets...")
    
    secrets_config = [
        ("ci-pipeline", "AWS_SECRET_KEY", "aws-secret-12345"),
        ("ci-pipeline", "DOCKER_PASSWORD", "docker-pass-xyz"),
        ("monitoring-agent", "DATADOG_API_KEY", "dd-api-key-abc"),
        ("backup-service", "ENCRYPTION_KEY", "enc-key-secure"),
        ("external-api", "CLIENT_SECRET", "client-secret-def"),
    ]
    
    for acc_name, secret_name, secret_value in secrets_config:
        account = next((a for a in accounts if a.name == acc_name), None)
        if account:
            secret = manager.store_secret(account.account_id, secret_name, secret_value)
            print(f"  🔒 {acc_name}/{secret_name}")
            
    # Validate some tokens
    print("\n✅ Validating Tokens...")
    
    validated = 0
    for token_id, raw_token in list(raw_tokens.items())[:5]:
        account = manager.validate_token(raw_token)
        if account:
            validated += 1
            
    print(f"  ✓ Validated {validated} tokens successfully")
    
    # Rotate a token
    print("\n🔄 Rotating Tokens...")
    
    token_to_rotate = created_tokens[0]
    new_token, new_raw = manager.rotate_token(token_to_rotate.token_id)
    if new_token:
        print(f"  ✓ Rotated token {token_to_rotate.token_prefix}... -> {new_token.token_prefix}...")
        
    # Revoke a token
    print("\n❌ Revoking Tokens...")
    
    token_to_revoke = created_tokens[1]
    manager.revoke_token(token_to_revoke.token_id)
    print(f"  ✓ Revoked token {token_to_revoke.token_prefix}...")
    
    # Check expiring tokens
    print("\n⏰ Checking Expiring Tokens...")
    
    expiring = manager.get_expiring_tokens(days=30)
    print(f"  Tokens expiring in next 30 days: {len(expiring)}")
    
    # Display accounts
    print("\n👤 Service Accounts:")
    
    print("\n  ┌──────────────────────────┬──────────────┬────────────┬──────────┐")
    print("  │ Account                  │ Type         │ Project    │ Tokens   │")
    print("  ├──────────────────────────┼──────────────┼────────────┼──────────┤")
    
    for acc in manager.accounts.values():
        name = acc.name[:24].ljust(24)
        acc_type = acc.account_type.value[:12].ljust(12)
        project = acc.project[:10].ljust(10)
        tokens = str(acc.active_tokens)[:8].ljust(8)
        
        print(f"  │ {name} │ {acc_type} │ {project} │ {tokens} │")
        
    print("  └──────────────────────────┴──────────────┴────────────┴──────────┘")
    
    # Display tokens
    print("\n🔑 Active Tokens:")
    
    print("\n  ┌──────────────────────────┬──────────┬─────────────────┬─────────┐")
    print("  │ Token Name               │ Type     │ Expires         │ Status  │")
    print("  ├──────────────────────────┼──────────┼─────────────────┼─────────┤")
    
    for token in list(manager.tokens.values())[:8]:
        name = token.name[:24].ljust(24)
        token_type = token.token_type.value[:8].ljust(8)
        
        if token.expires_at:
            expires = token.expires_at.strftime("%Y-%m-%d")[:15].ljust(15)
        else:
            expires = "Never".ljust(15)
            
        status_icons = {
            TokenStatus.ACTIVE: "🟢",
            TokenStatus.REVOKED: "🔴",
            TokenStatus.EXPIRED: "⚫",
            TokenStatus.ROTATED: "🔄"
        }
        status = status_icons.get(token.status, "⚪")[:7].ljust(7)
        
        print(f"  │ {name} │ {token_type} │ {expires} │ {status} │")
        
    print("  └──────────────────────────┴──────────┴─────────────────┴─────────┘")
    
    # Permission sets
    print("\n🛡️ Permission Sets:")
    
    for pset in manager.permission_sets.values():
        print(f"  📋 {pset.name}")
        for perm in pset.permissions[:2]:
            print(f"     └─ {perm.resource}: {perm.scope.value}")
            
    # Audit log
    print("\n📜 Recent Audit Log:")
    
    for entry in manager.audit_log[-5:]:
        acc = manager.accounts.get(entry.account_id)
        acc_name = acc.name if acc else "unknown"
        
        action_icons = {
            "create_account": "➕",
            "create_token": "🔑",
            "rotate_token": "🔄",
            "revoke_token": "❌",
            "store_secret": "🔐"
        }
        icon = action_icons.get(entry.action, "📝")
        
        print(f"  {icon} {entry.action}: {acc_name}")
        print(f"     {entry.timestamp.strftime('%H:%M:%S')} from {entry.source_ip}")
        
    # Statistics
    print("\n📊 Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Accounts: {stats['total_accounts']} (active: {stats['active_accounts']})")
    print(f"  Tokens: {stats['total_tokens']} (active: {stats['active_tokens']})")
    print(f"  Secrets: {stats['secrets']}")
    print(f"  Audit Entries: {stats['audit_entries']}")
    
    # By type
    print("\n  By Account Type:")
    type_icons = {"service": "🔧", "bot": "🤖", "ci_cd": "⚙️", "external": "🌐"}
    for t, count in stats['accounts_by_type'].items():
        icon = type_icons.get(t, "📋")
        bar = "█" * count + "░" * (8 - count)
        print(f"    {icon} {t:10s} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Service Accounts Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Accounts:                {stats['total_accounts']:>12}                        │")
    print(f"│ Active Accounts:               {stats['active_accounts']:>12}                        │")
    print(f"│ Active Tokens:                 {stats['active_tokens']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Secrets Stored:                {stats['secrets']:>12}                        │")
    print(f"│ Audit Entries:                 {stats['audit_entries']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Service Accounts Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
