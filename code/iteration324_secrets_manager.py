#!/usr/bin/env python3
"""
Server Init - Iteration 324: Secrets Manager Platform
Платформа управления секретами

Функционал:
- Secret Storage - безопасное хранение секретов
- Dynamic Secrets - динамические секреты
- Secret Rotation - ротация секретов
- Access Control - контроль доступа
- Encryption - шифрование
- Audit Logging - аудит доступа
- Secret Versioning - версионирование секретов
- Integration APIs - интеграционные API
"""

import asyncio
import random
import hashlib
import base64
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class SecretType(Enum):
    """Тип секрета"""
    PASSWORD = "password"
    API_KEY = "api_key"
    SSH_KEY = "ssh_key"
    CERTIFICATE = "certificate"
    DATABASE_CREDENTIAL = "database_credential"
    AWS_CREDENTIAL = "aws_credential"
    TOKEN = "token"
    ENCRYPTION_KEY = "encryption_key"
    GENERIC = "generic"


class SecretEngine(Enum):
    """Движок секретов"""
    KV = "kv"  # Key-Value
    DATABASE = "database"
    AWS = "aws"
    PKI = "pki"
    SSH = "ssh"
    TRANSIT = "transit"


class AccessType(Enum):
    """Тип доступа"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    ROTATE = "rotate"


class AuditAction(Enum):
    """Действие аудита"""
    SECRET_READ = "secret_read"
    SECRET_WRITE = "secret_write"
    SECRET_DELETE = "secret_delete"
    SECRET_ROTATE = "secret_rotate"
    POLICY_CREATE = "policy_create"
    POLICY_UPDATE = "policy_update"
    TOKEN_CREATE = "token_create"
    TOKEN_REVOKE = "token_revoke"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"


class RotationStrategy(Enum):
    """Стратегия ротации"""
    TIME_BASED = "time_based"
    ON_DEMAND = "on_demand"
    USAGE_BASED = "usage_based"
    AUTOMATIC = "automatic"


@dataclass
class SecretVersion:
    """Версия секрета"""
    version_id: str
    version_number: int
    
    # Encrypted value
    encrypted_value: str = ""
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Status
    is_current: bool = True
    is_destroyed: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    destroyed_at: Optional[datetime] = None


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    path: str  # e.g., "secret/data/myapp/config"
    
    # Name
    name: str = ""
    description: str = ""
    
    # Type
    secret_type: SecretType = SecretType.GENERIC
    
    # Engine
    engine: SecretEngine = SecretEngine.KV
    
    # Versions
    version_ids: List[str] = field(default_factory=list)
    current_version: int = 0
    max_versions: int = 10
    
    # Rotation
    rotation_enabled: bool = False
    rotation_period_days: int = 90
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Access
    access_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class DynamicSecret:
    """Динамический секрет"""
    dynamic_id: str
    role_name: str
    
    # Engine
    engine: SecretEngine = SecretEngine.DATABASE
    
    # Generated credentials
    username: str = ""
    password: str = ""
    
    # TTL
    ttl_seconds: int = 3600
    max_ttl_seconds: int = 86400
    
    # Lease
    lease_id: str = ""
    lease_duration: int = 0
    renewable: bool = True
    
    # Status
    is_revoked: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    name: str
    
    # Path rules
    path_rules: List[Dict[str, Any]] = field(default_factory=list)
    # Format: {"path": "secret/data/*", "capabilities": ["read", "list"]}
    
    # Description
    description: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessToken:
    """Токен доступа"""
    token_id: str
    
    # Token (hashed)
    token_hash: str = ""
    
    # Display name
    display_name: str = ""
    
    # Policies
    policy_ids: List[str] = field(default_factory=list)
    
    # TTL
    ttl_seconds: int = 3600
    explicit_max_ttl: int = 0
    
    # Renewal
    renewable: bool = True
    num_uses: int = 0  # 0 = unlimited
    uses_remaining: int = 0
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Status
    is_revoked: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))


@dataclass
class RotationConfig:
    """Конфигурация ротации"""
    config_id: str
    secret_path: str
    
    # Strategy
    strategy: RotationStrategy = RotationStrategy.TIME_BASED
    
    # Schedule
    rotation_period_days: int = 90
    cron_schedule: str = ""
    
    # Options
    auto_rotate: bool = True
    notify_before_days: int = 7
    
    # History
    rotation_count: int = 0
    last_rotation: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Status
    is_enabled: bool = True


@dataclass
class AuditEntry:
    """Запись аудита"""
    audit_id: str
    
    # Action
    action: AuditAction = AuditAction.SECRET_READ
    
    # Target
    path: str = ""
    
    # Actor
    token_id: str = ""
    client_ip: str = ""
    user_agent: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptionKey:
    """Ключ шифрования"""
    key_id: str
    name: str
    
    # Key type
    key_type: str = "aes256-gcm96"
    
    # Version
    version: int = 1
    min_decryption_version: int = 1
    min_encryption_version: int = 1
    
    # Options
    derived: bool = False
    exportable: bool = False
    allow_plaintext_backup: bool = False
    
    # Status
    supports_encryption: bool = True
    supports_decryption: bool = True
    supports_derivation: bool = False
    supports_signing: bool = False
    
    # Usage
    encryption_count: int = 0
    decryption_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecretLease:
    """Аренда секрета"""
    lease_id: str
    
    # Secret
    secret_path: str = ""
    dynamic_id: str = ""
    
    # Duration
    lease_duration: int = 3600
    
    # Renewal
    renewable: bool = True
    renewal_count: int = 0
    max_renewals: int = 10
    
    # Timestamps
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))


class SecretsManager:
    """Менеджер секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        self.secret_versions: Dict[str, SecretVersion] = {}
        self.dynamic_secrets: Dict[str, DynamicSecret] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.tokens: Dict[str, AccessToken] = {}
        self.rotation_configs: Dict[str, RotationConfig] = {}
        self.audit_log: List[AuditEntry] = []
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.leases: Dict[str, SecretLease] = {}
        
        # Master key for encryption (in production, this would be handled by HSM)
        self._master_key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        
    def _encrypt(self, plaintext: str) -> str:
        """Шифрование (упрощенное)"""
        # In production, use proper encryption (AES-GCM)
        combined = f"{self._master_key}:{plaintext}"
        return base64.b64encode(combined.encode()).decode()
        
    def _decrypt(self, ciphertext: str) -> str:
        """Дешифрование (упрощенное)"""
        decoded = base64.b64decode(ciphertext.encode()).decode()
        return decoded.split(":", 1)[1] if ":" in decoded else ""
        
    def _generate_password(self, length: int = 32) -> str:
        """Генерация пароля"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return "".join(random.choice(chars) for _ in range(length))
        
    def _log_audit(self, action: AuditAction, path: str,
                  token_id: str = "", success: bool = True,
                  error_message: str = "", metadata: Dict = None):
        """Запись в аудит"""
        entry = AuditEntry(
            audit_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            path=path,
            token_id=token_id,
            success=success,
            error_message=error_message,
            client_ip=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            metadata=metadata or {}
        )
        self.audit_log.append(entry)
        
    async def create_secret(self, path: str,
                           value: str,
                           secret_type: SecretType = SecretType.GENERIC,
                           name: str = "",
                           description: str = "",
                           metadata: Dict[str, str] = None,
                           ttl_days: int = 0) -> Secret:
        """Создание секрета"""
        secret = Secret(
            secret_id=f"sec_{uuid.uuid4().hex[:8]}",
            path=path,
            name=name or path.split("/")[-1],
            description=description,
            secret_type=secret_type
        )
        
        if ttl_days > 0:
            secret.expires_at = datetime.now() + timedelta(days=ttl_days)
            
        # Create first version
        version = SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version_number=1,
            encrypted_value=self._encrypt(value),
            metadata=metadata or {}
        )
        
        self.secret_versions[version.version_id] = version
        secret.version_ids.append(version.version_id)
        secret.current_version = 1
        
        self.secrets[secret.secret_id] = secret
        
        self._log_audit(AuditAction.SECRET_WRITE, path)
        
        return secret
        
    async def read_secret(self, path: str, version: int = 0) -> Optional[Dict[str, Any]]:
        """Чтение секрета"""
        secret = None
        for s in self.secrets.values():
            if s.path == path:
                secret = s
                break
                
        if not secret:
            self._log_audit(AuditAction.SECRET_READ, path, success=False, error_message="Not found")
            return None
            
        # Get version
        target_version = version if version > 0 else secret.current_version
        
        for ver_id in secret.version_ids:
            ver = self.secret_versions.get(ver_id)
            if ver and ver.version_number == target_version and not ver.is_destroyed:
                secret.access_count += 1
                
                self._log_audit(AuditAction.SECRET_READ, path)
                
                return {
                    "path": path,
                    "value": self._decrypt(ver.encrypted_value),
                    "version": ver.version_number,
                    "metadata": ver.metadata,
                    "created_at": ver.created_at.isoformat()
                }
                
        return None
        
    async def update_secret(self, path: str,
                           value: str,
                           metadata: Dict[str, str] = None) -> Optional[Secret]:
        """Обновление секрета"""
        secret = None
        for s in self.secrets.values():
            if s.path == path:
                secret = s
                break
                
        if not secret:
            return None
            
        # Create new version
        new_version_num = secret.current_version + 1
        
        version = SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version_number=new_version_num,
            encrypted_value=self._encrypt(value),
            metadata=metadata or {}
        )
        
        # Mark old version as not current
        for ver_id in secret.version_ids:
            ver = self.secret_versions.get(ver_id)
            if ver:
                ver.is_current = False
                
        self.secret_versions[version.version_id] = version
        secret.version_ids.append(version.version_id)
        secret.current_version = new_version_num
        secret.updated_at = datetime.now()
        
        # Clean up old versions if exceeding max
        while len(secret.version_ids) > secret.max_versions:
            old_ver_id = secret.version_ids.pop(0)
            if old_ver_id in self.secret_versions:
                self.secret_versions[old_ver_id].is_destroyed = True
                self.secret_versions[old_ver_id].destroyed_at = datetime.now()
                
        self._log_audit(AuditAction.SECRET_WRITE, path)
        
        return secret
        
    async def delete_secret(self, path: str) -> bool:
        """Удаление секрета"""
        secret_id = None
        for sid, s in self.secrets.items():
            if s.path == path:
                secret_id = sid
                break
                
        if not secret_id:
            return False
            
        secret = self.secrets[secret_id]
        
        # Destroy all versions
        for ver_id in secret.version_ids:
            if ver_id in self.secret_versions:
                self.secret_versions[ver_id].is_destroyed = True
                self.secret_versions[ver_id].destroyed_at = datetime.now()
                
        del self.secrets[secret_id]
        
        self._log_audit(AuditAction.SECRET_DELETE, path)
        
        return True
        
    async def rotate_secret(self, path: str) -> Optional[str]:
        """Ротация секрета"""
        secret = None
        for s in self.secrets.values():
            if s.path == path:
                secret = s
                break
                
        if not secret:
            return None
            
        # Generate new password
        new_value = self._generate_password()
        
        await self.update_secret(path, new_value)
        
        secret.last_rotated = datetime.now()
        if secret.rotation_period_days > 0:
            secret.next_rotation = datetime.now() + timedelta(days=secret.rotation_period_days)
            
        self._log_audit(AuditAction.SECRET_ROTATE, path)
        
        return new_value
        
    async def generate_dynamic_secret(self, role_name: str,
                                     engine: SecretEngine = SecretEngine.DATABASE,
                                     ttl_seconds: int = 3600) -> DynamicSecret:
        """Генерация динамического секрета"""
        username = f"{role_name}_{uuid.uuid4().hex[:8]}"
        password = self._generate_password()
        
        dynamic = DynamicSecret(
            dynamic_id=f"dyn_{uuid.uuid4().hex[:8]}",
            role_name=role_name,
            engine=engine,
            username=username,
            password=password,
            ttl_seconds=ttl_seconds,
            lease_id=f"lease_{uuid.uuid4().hex[:8]}",
            lease_duration=ttl_seconds,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds)
        )
        
        # Create lease
        lease = SecretLease(
            lease_id=dynamic.lease_id,
            dynamic_id=dynamic.dynamic_id,
            lease_duration=ttl_seconds,
            expires_at=dynamic.expires_at
        )
        
        self.leases[lease.lease_id] = lease
        self.dynamic_secrets[dynamic.dynamic_id] = dynamic
        
        return dynamic
        
    async def revoke_dynamic_secret(self, dynamic_id: str) -> bool:
        """Отзыв динамического секрета"""
        dynamic = self.dynamic_secrets.get(dynamic_id)
        if not dynamic:
            return False
            
        dynamic.is_revoked = True
        
        # Revoke lease
        if dynamic.lease_id in self.leases:
            del self.leases[dynamic.lease_id]
            
        return True
        
    async def create_policy(self, name: str,
                           path_rules: List[Dict[str, Any]],
                           description: str = "") -> AccessPolicy:
        """Создание политики доступа"""
        policy = AccessPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            path_rules=path_rules,
            description=description
        )
        
        self.policies[policy.policy_id] = policy
        
        self._log_audit(AuditAction.POLICY_CREATE, f"policy/{name}")
        
        return policy
        
    async def create_token(self, display_name: str,
                          policy_ids: List[str],
                          ttl_seconds: int = 3600,
                          num_uses: int = 0,
                          metadata: Dict[str, str] = None) -> AccessToken:
        """Создание токена"""
        token_value = uuid.uuid4().hex
        token_hash = hashlib.sha256(token_value.encode()).hexdigest()
        
        token = AccessToken(
            token_id=f"tok_{uuid.uuid4().hex[:8]}",
            token_hash=token_hash,
            display_name=display_name,
            policy_ids=policy_ids,
            ttl_seconds=ttl_seconds,
            num_uses=num_uses,
            uses_remaining=num_uses if num_uses > 0 else -1,
            metadata=metadata or {},
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds)
        )
        
        self.tokens[token.token_id] = token
        
        self._log_audit(AuditAction.TOKEN_CREATE, f"token/{token.token_id}")
        
        # Return with actual token (only time it's available)
        token.metadata["token"] = token_value
        
        return token
        
    async def revoke_token(self, token_id: str) -> bool:
        """Отзыв токена"""
        token = self.tokens.get(token_id)
        if not token:
            return False
            
        token.is_revoked = True
        
        self._log_audit(AuditAction.TOKEN_REVOKE, f"token/{token_id}")
        
        return True
        
    async def create_encryption_key(self, name: str,
                                   key_type: str = "aes256-gcm96",
                                   exportable: bool = False) -> EncryptionKey:
        """Создание ключа шифрования"""
        key = EncryptionKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            name=name,
            key_type=key_type,
            exportable=exportable
        )
        
        self.encryption_keys[key.key_id] = key
        return key
        
    async def encrypt_data(self, key_name: str, plaintext: str) -> Optional[str]:
        """Шифрование данных через Transit"""
        key = None
        for k in self.encryption_keys.values():
            if k.name == key_name and k.supports_encryption:
                key = k
                break
                
        if not key:
            return None
            
        key.encryption_count += 1
        
        # Return base64 encoded "ciphertext"
        return f"vault:v{key.version}:{base64.b64encode(plaintext.encode()).decode()}"
        
    async def decrypt_data(self, key_name: str, ciphertext: str) -> Optional[str]:
        """Дешифрование данных через Transit"""
        key = None
        for k in self.encryption_keys.values():
            if k.name == key_name and k.supports_decryption:
                key = k
                break
                
        if not key:
            return None
            
        key.decryption_count += 1
        
        # Parse ciphertext
        parts = ciphertext.split(":")
        if len(parts) >= 3:
            return base64.b64decode(parts[2]).decode()
            
        return None
        
    async def setup_rotation(self, secret_path: str,
                            rotation_period_days: int = 90,
                            auto_rotate: bool = True) -> RotationConfig:
        """Настройка ротации"""
        config = RotationConfig(
            config_id=f"rot_{uuid.uuid4().hex[:8]}",
            secret_path=secret_path,
            rotation_period_days=rotation_period_days,
            auto_rotate=auto_rotate,
            next_rotation=datetime.now() + timedelta(days=rotation_period_days)
        )
        
        # Update secret
        for s in self.secrets.values():
            if s.path == secret_path:
                s.rotation_enabled = True
                s.rotation_period_days = rotation_period_days
                s.next_rotation = config.next_rotation
                break
                
        self.rotation_configs[config.config_id] = config
        return config
        
    async def renew_lease(self, lease_id: str, increment_seconds: int = 3600) -> Optional[SecretLease]:
        """Продление аренды"""
        lease = self.leases.get(lease_id)
        if not lease or not lease.renewable:
            return None
            
        if lease.renewal_count >= lease.max_renewals:
            return None
            
        lease.expires_at = datetime.now() + timedelta(seconds=increment_seconds)
        lease.renewal_count += 1
        
        # Update dynamic secret if exists
        dynamic = self.dynamic_secrets.get(lease.dynamic_id)
        if dynamic:
            dynamic.expires_at = lease.expires_at
            
        return lease
        
    def check_access(self, token_id: str, path: str, action: AccessType) -> bool:
        """Проверка доступа"""
        token = self.tokens.get(token_id)
        if not token or token.is_revoked:
            return False
            
        if token.expires_at < datetime.now():
            return False
            
        # Check policies
        for policy_id in token.policy_ids:
            policy = self.policies.get(policy_id)
            if not policy or not policy.is_active:
                continue
                
            for rule in policy.path_rules:
                rule_path = rule.get("path", "")
                capabilities = rule.get("capabilities", [])
                
                # Check path match (simplified glob matching)
                if rule_path.endswith("*"):
                    if path.startswith(rule_path[:-1]):
                        if action.value in capabilities or "*" in capabilities:
                            return True
                elif rule_path == path:
                    if action.value in capabilities or "*" in capabilities:
                        return True
                        
        return False
        
    def get_audit_log(self, action: AuditAction = None,
                      path: str = None,
                      limit: int = 100) -> List[AuditEntry]:
        """Получение логов аудита"""
        filtered = self.audit_log
        
        if action:
            filtered = [e for e in filtered if e.action == action]
            
        if path:
            filtered = [e for e in filtered if path in e.path]
            
        return sorted(filtered, key=lambda e: e.timestamp, reverse=True)[:limit]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_secrets = len(self.secrets)
        total_versions = len(self.secret_versions)
        active_versions = sum(1 for v in self.secret_versions.values() if not v.is_destroyed)
        
        by_type = {}
        for s in self.secrets.values():
            by_type[s.secret_type.value] = by_type.get(s.secret_type.value, 0) + 1
            
        total_dynamic = len(self.dynamic_secrets)
        active_dynamic = sum(1 for d in self.dynamic_secrets.values() if not d.is_revoked and d.expires_at > datetime.now())
        
        total_tokens = len(self.tokens)
        active_tokens = sum(1 for t in self.tokens.values() if not t.is_revoked and t.expires_at > datetime.now())
        
        total_leases = len(self.leases)
        active_leases = sum(1 for l in self.leases.values() if l.expires_at > datetime.now())
        
        total_access = sum(s.access_count for s in self.secrets.values())
        
        rotation_due = sum(1 for s in self.secrets.values() if s.next_rotation and s.next_rotation < datetime.now())
        
        return {
            "total_secrets": total_secrets,
            "total_versions": total_versions,
            "active_versions": active_versions,
            "by_type": by_type,
            "total_dynamic_secrets": total_dynamic,
            "active_dynamic_secrets": active_dynamic,
            "total_policies": len(self.policies),
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "total_leases": total_leases,
            "active_leases": active_leases,
            "encryption_keys": len(self.encryption_keys),
            "rotation_configs": len(self.rotation_configs),
            "rotation_due": rotation_due,
            "total_access_count": total_access,
            "audit_entries": len(self.audit_log)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 324: Secrets Manager Platform")
    print("=" * 60)
    
    secrets_mgr = SecretsManager()
    print("✓ Secrets Manager created")
    
    # Create secrets
    print("\n🔐 Creating Secrets...")
    
    secrets_data = [
        ("secret/data/app/database", "SuperSecretPassword123!", SecretType.DATABASE_CREDENTIAL, "Database password"),
        ("secret/data/app/api-key", "sk_live_abc123xyz789", SecretType.API_KEY, "Production API key"),
        ("secret/data/app/jwt-secret", "jwt_secret_key_very_long_string", SecretType.TOKEN, "JWT signing key"),
        ("secret/data/infra/ssh-key", "-----BEGIN RSA PRIVATE KEY-----...", SecretType.SSH_KEY, "SSH key for servers"),
        ("secret/data/infra/aws", "AKIAIOSFODNN7EXAMPLE", SecretType.AWS_CREDENTIAL, "AWS credentials"),
        ("secret/data/app/encryption-key", "aes256_master_key_32_bytes_long", SecretType.ENCRYPTION_KEY, "Data encryption key"),
        ("secret/data/app/smtp-password", "smtp_password_123", SecretType.PASSWORD, "SMTP server password"),
        ("secret/data/app/redis-auth", "redis_auth_token", SecretType.PASSWORD, "Redis auth token")
    ]
    
    secrets = []
    for path, value, secret_type, desc in secrets_data:
        secret = await secrets_mgr.create_secret(
            path, value, secret_type,
            description=desc,
            metadata={"environment": "production", "owner": "platform-team"}
        )
        secrets.append(secret)
        print(f"  🔐 {path} ({secret_type.value})")
        
    # Update some secrets (create versions)
    print("\n📝 Creating Secret Versions...")
    
    for secret in secrets[:3]:
        for i in range(3):
            await secrets_mgr.update_secret(
                secret.path,
                f"new_value_version_{i+2}",
                {"update_reason": f"rotation_{i+1}"}
            )
            
    print(f"  ✓ Created multiple versions for 3 secrets")
    
    # Setup rotation
    print("\n🔄 Setting Up Secret Rotation...")
    
    rotation_configs = []
    for secret in secrets[:5]:
        config = await secrets_mgr.setup_rotation(
            secret.path,
            rotation_period_days=30,
            auto_rotate=True
        )
        rotation_configs.append(config)
        print(f"  🔄 Rotation enabled for {secret.path}")
        
    # Rotate a secret
    print("\n🔄 Rotating Secret...")
    
    new_password = await secrets_mgr.rotate_secret(secrets[0].path)
    if new_password:
        print(f"  ✓ Secret rotated, new value: {new_password[:8]}...")
        
    # Generate dynamic secrets
    print("\n⚡ Generating Dynamic Secrets...")
    
    dynamic_roles = [
        ("db-readonly", SecretEngine.DATABASE),
        ("db-readwrite", SecretEngine.DATABASE),
        ("aws-s3-access", SecretEngine.AWS),
        ("pki-issuer", SecretEngine.PKI)
    ]
    
    dynamic_secrets = []
    for role, engine in dynamic_roles:
        dynamic = await secrets_mgr.generate_dynamic_secret(role, engine, 3600)
        dynamic_secrets.append(dynamic)
        print(f"  ⚡ {role}: {dynamic.username}")
        
    # Create policies
    print("\n📋 Creating Access Policies...")
    
    policies_data = [
        ("admin-policy", [
            {"path": "secret/data/*", "capabilities": ["read", "write", "delete", "list"]},
            {"path": "auth/*", "capabilities": ["*"]}
        ]),
        ("app-readonly", [
            {"path": "secret/data/app/*", "capabilities": ["read", "list"]}
        ]),
        ("infra-team", [
            {"path": "secret/data/infra/*", "capabilities": ["read", "write", "list"]}
        ]),
        ("ci-cd", [
            {"path": "secret/data/app/*", "capabilities": ["read"]},
            {"path": "secret/data/infra/aws", "capabilities": ["read"]}
        ])
    ]
    
    policies = []
    for name, rules in policies_data:
        policy = await secrets_mgr.create_policy(name, rules, f"Policy for {name}")
        policies.append(policy)
        print(f"  📋 {name}")
        
    # Create tokens
    print("\n🎫 Creating Access Tokens...")
    
    tokens_data = [
        ("admin-token", [policies[0].policy_id], 86400),
        ("app-token", [policies[1].policy_id], 3600),
        ("infra-token", [policies[2].policy_id], 7200),
        ("ci-token", [policies[3].policy_id], 3600)
    ]
    
    tokens = []
    for name, policy_ids, ttl in tokens_data:
        token = await secrets_mgr.create_token(name, policy_ids, ttl)
        tokens.append(token)
        print(f"  🎫 {name} (TTL: {ttl}s)")
        
    # Create encryption keys
    print("\n🔑 Creating Encryption Keys...")
    
    keys_data = [
        ("app-encryption", "aes256-gcm96"),
        ("backup-encryption", "aes256-gcm96"),
        ("signing-key", "ed25519")
    ]
    
    enc_keys = []
    for name, key_type in keys_data:
        key = await secrets_mgr.create_encryption_key(name, key_type)
        enc_keys.append(key)
        print(f"  🔑 {name} ({key_type})")
        
    # Encrypt/Decrypt data
    print("\n🔒 Transit Encryption Demo...")
    
    plaintext = "Sensitive data to encrypt"
    ciphertext = await secrets_mgr.encrypt_data("app-encryption", plaintext)
    print(f"  Plaintext:  {plaintext}")
    print(f"  Ciphertext: {ciphertext[:50]}...")
    
    decrypted = await secrets_mgr.decrypt_data("app-encryption", ciphertext)
    print(f"  Decrypted:  {decrypted}")
    
    # Read secrets
    print("\n📖 Reading Secrets...")
    
    for secret in secrets[:3]:
        data = await secrets_mgr.read_secret(secret.path)
        if data:
            print(f"  📖 {data['path']} (v{data['version']})")
            
    # Access check demo
    print("\n🔐 Access Control Demo...")
    
    checks = [
        (tokens[0].token_id, "secret/data/app/database", AccessType.READ),
        (tokens[1].token_id, "secret/data/app/database", AccessType.READ),
        (tokens[1].token_id, "secret/data/infra/ssh-key", AccessType.READ),
        (tokens[2].token_id, "secret/data/infra/ssh-key", AccessType.WRITE)
    ]
    
    for token_id, path, action in checks:
        token = secrets_mgr.tokens.get(token_id)
        token_name = token.display_name if token else "unknown"
        result = secrets_mgr.check_access(token_id, path, action)
        status = "✓ Allowed" if result else "✗ Denied"
        print(f"  {token_name} -> {path} ({action.value}): {status}")
        
    # Lease management
    print("\n📜 Lease Management...")
    
    for dynamic in dynamic_secrets[:2]:
        print(f"\n  📜 Lease: {dynamic.lease_id[:20]}...")
        print(f"     Duration: {dynamic.lease_duration}s")
        print(f"     Expires: {dynamic.expires_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Renew lease
        renewed = await secrets_mgr.renew_lease(dynamic.lease_id, 7200)
        if renewed:
            print(f"     ✓ Renewed, new expiry: {renewed.expires_at.strftime('%Y-%m-%d %H:%M')}")
            
    # Secret status
    print("\n🔐 Secret Status:")
    
    print("\n  ┌─────────────────────────────────────────────────┬────────────────────────┬────────────────┬────────────────┬──────────────┐")
    print("  │ Path                                            │ Type                   │ Versions       │ Access Count   │ Rotation     │")
    print("  ├─────────────────────────────────────────────────┼────────────────────────┼────────────────┼────────────────┼──────────────┤")
    
    for secret in secrets:
        path = secret.path[:47].ljust(47)
        s_type = secret.secret_type.value[:22].ljust(22)
        versions = str(secret.current_version)[:14].ljust(14)
        access = str(secret.access_count)[:14].ljust(14)
        rotation = ("✓ Enabled" if secret.rotation_enabled else "✗ Disabled")[:12].ljust(12)
        
        print(f"  │ {path} │ {s_type} │ {versions} │ {access} │ {rotation} │")
        
    print("  └─────────────────────────────────────────────────┴────────────────────────┴────────────────┴────────────────┴──────────────┘")
    
    # Dynamic secrets status
    print("\n⚡ Dynamic Secrets:")
    
    for dynamic in dynamic_secrets:
        status = "Active" if not dynamic.is_revoked and dynamic.expires_at > datetime.now() else "Expired"
        ttl = int((dynamic.expires_at - datetime.now()).total_seconds()) if dynamic.expires_at > datetime.now() else 0
        
        print(f"\n  ⚡ Role: {dynamic.role_name}")
        print(f"     Username: {dynamic.username}")
        print(f"     Engine: {dynamic.engine.value}")
        print(f"     TTL: {ttl}s remaining")
        print(f"     Status: {status}")
        
    # Token status
    print("\n🎫 Token Status:")
    
    print("\n  ┌────────────────────────┬────────────────────────────────┬──────────────┬────────────────┬──────────────┐")
    print("  │ Token                  │ Policies                       │ TTL          │ Expires        │ Status       │")
    print("  ├────────────────────────┼────────────────────────────────┼──────────────┼────────────────┼──────────────┤")
    
    for token in tokens:
        name = token.display_name[:22].ljust(22)
        
        policy_names = []
        for pid in token.policy_ids:
            p = secrets_mgr.policies.get(pid)
            if p:
                policy_names.append(p.name)
        policies_str = ", ".join(policy_names)[:30].ljust(30)
        
        ttl = f"{token.ttl_seconds}s"[:12].ljust(12)
        expires = token.expires_at.strftime("%H:%M:%S")[:14].ljust(14)
        status = ("✓ Active" if not token.is_revoked else "✗ Revoked")[:12].ljust(12)
        
        print(f"  │ {name} │ {policies_str} │ {ttl} │ {expires} │ {status} │")
        
    print("  └────────────────────────┴────────────────────────────────┴──────────────┴────────────────┴──────────────┘")
    
    # Encryption keys
    print("\n🔑 Encryption Keys:")
    
    for key in enc_keys:
        print(f"\n  🔑 {key.name}")
        print(f"     Type: {key.key_type}")
        print(f"     Version: {key.version}")
        print(f"     Encryptions: {key.encryption_count}")
        print(f"     Decryptions: {key.decryption_count}")
        
    # Audit log
    print("\n📝 Recent Audit Log:")
    
    recent_audit = secrets_mgr.get_audit_log(limit=10)
    
    for entry in recent_audit[:10]:
        status = "✓" if entry.success else "✗"
        timestamp = entry.timestamp.strftime("%H:%M:%S")
        
        print(f"  {timestamp} [{status}] {entry.action.value:20} {entry.path[:40]}")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    stats = secrets_mgr.get_statistics()
    
    print(f"\n  Secrets: {stats['total_secrets']}")
    print(f"  Versions: {stats['active_versions']}/{stats['total_versions']} active")
    print(f"  Dynamic Secrets: {stats['active_dynamic_secrets']}/{stats['total_dynamic_secrets']} active")
    print(f"  Tokens: {stats['active_tokens']}/{stats['total_tokens']} active")
    print(f"  Leases: {stats['active_leases']}/{stats['total_leases']} active")
    print(f"  Policies: {stats['total_policies']}")
    print(f"  Encryption Keys: {stats['encryption_keys']}")
    print(f"  Total Access Count: {stats['total_access_count']}")
    print(f"  Audit Entries: {stats['audit_entries']}")
    
    print("\n  By Secret Type:")
    for s_type, count in stats['by_type'].items():
        print(f"    {s_type}: {count}")
        
    if stats['rotation_due'] > 0:
        print(f"\n  ⚠️ {stats['rotation_due']} secrets due for rotation")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Secrets Manager Platform                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Secrets:               {stats['total_secrets']:>12}                          │")
    print(f"│ Active Versions:             {stats['active_versions']:>12}                          │")
    print(f"│ Active Tokens:               {stats['active_tokens']:>12}                          │")
    print(f"│ Active Dynamic Secrets:      {stats['active_dynamic_secrets']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Encryption Keys:             {stats['encryption_keys']:>12}                          │")
    print(f"│ Total Access Count:          {stats['total_access_count']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Secrets Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
