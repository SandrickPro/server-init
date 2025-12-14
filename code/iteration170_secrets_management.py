#!/usr/bin/env python3
"""
Server Init - Iteration 170: Secrets Management Platform
Платформа управления секретами

Функционал:
- Secret Storage - хранение секретов
- Secret Versioning - версионирование секретов
- Secret Rotation - ротация секретов
- Access Control - контроль доступа
- Encryption - шифрование
- Audit Logging - логирование аудита
- Dynamic Secrets - динамические секреты
- Secret Injection - внедрение секретов
"""

import asyncio
import base64
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
from collections import defaultdict
import json


class SecretType(Enum):
    """Тип секрета"""
    PASSWORD = "password"
    API_KEY = "api_key"
    TOKEN = "token"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"
    SSH_KEY = "ssh_key"
    GENERIC = "generic"


class SecretStatus(Enum):
    """Статус секрета"""
    ACTIVE = "active"
    ROTATED = "rotated"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class AccessLevel(Enum):
    """Уровень доступа"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    ROTATE = "rotate"


class AuditAction(Enum):
    """Действие аудита"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ROTATE = "rotate"
    REVOKE = "revoke"
    ACCESS_DENIED = "access_denied"


@dataclass
class SecretVersion:
    """Версия секрета"""
    version_id: str
    version_number: int = 1
    
    # Value (encrypted)
    encrypted_value: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # Status
    status: SecretStatus = SecretStatus.ACTIVE
    
    # Expiration
    expires_at: Optional[datetime] = None


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    name: str = ""
    path: str = ""  # e.g., /production/database/password
    
    # Type
    secret_type: SecretType = SecretType.GENERIC
    
    # Versions
    versions: List[SecretVersion] = field(default_factory=list)
    current_version: int = 0
    max_versions: int = 10
    
    # Metadata
    description: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Rotation
    rotation_enabled: bool = False
    rotation_interval_days: int = 30
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Access stats
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    name: str = ""
    
    # Path pattern (supports wildcards)
    path_pattern: str = "*"
    
    # Allowed identities
    allowed_services: List[str] = field(default_factory=list)
    allowed_roles: List[str] = field(default_factory=list)
    
    # Permissions
    permissions: List[AccessLevel] = field(default_factory=list)
    
    # Conditions
    ip_whitelist: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, str] = field(default_factory=dict)  # start_hour, end_hour
    
    # Status
    enabled: bool = True


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Action
    action: AuditAction = AuditAction.READ
    
    # Target
    secret_path: str = ""
    secret_version: int = 0
    
    # Actor
    actor_id: str = ""
    actor_type: str = ""  # service, user, system
    
    # Context
    source_ip: str = ""
    user_agent: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""


@dataclass
class DynamicSecretConfig:
    """Конфигурация динамического секрета"""
    config_id: str
    name: str = ""
    
    # Backend
    backend_type: str = ""  # database, aws, kubernetes
    backend_config: Dict[str, str] = field(default_factory=dict)
    
    # Lease
    default_ttl_sec: int = 3600
    max_ttl_sec: int = 86400
    
    # Template
    secret_template: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecretLease:
    """Аренда динамического секрета"""
    lease_id: str
    config_id: str = ""
    
    # Value
    secret_value: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    
    # Renewal
    renewable: bool = True
    renewals_count: int = 0
    
    # Client
    client_id: str = ""


class EncryptionEngine:
    """Движок шифрования"""
    
    def __init__(self, master_key: str = None):
        # In production, use proper KMS
        self.master_key = master_key or secrets.token_hex(32)
        
    def encrypt(self, plaintext: str) -> str:
        """Шифрование"""
        # Simple XOR encryption for demo (use AES in production)
        key_bytes = self.master_key.encode()[:len(plaintext)]
        encrypted = bytes(a ^ b for a, b in zip(plaintext.encode(), key_bytes * (len(plaintext) // len(key_bytes) + 1)))
        return base64.b64encode(encrypted).decode()
        
    def decrypt(self, ciphertext: str) -> str:
        """Дешифрование"""
        encrypted = base64.b64decode(ciphertext)
        key_bytes = self.master_key.encode()[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_bytes * (len(encrypted) // len(key_bytes) + 1)))
        return decrypted.decode()
        
    def hash_secret(self, value: str) -> str:
        """Хеширование секрета"""
        return hashlib.sha256(value.encode()).hexdigest()


class SecretGenerator:
    """Генератор секретов"""
    
    @staticmethod
    def generate_password(length: int = 32, include_special: bool = True) -> str:
        """Генерация пароля"""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*()_+-="
        return ''.join(secrets.choice(chars) for _ in range(length))
        
    @staticmethod
    def generate_api_key(prefix: str = "sk") -> str:
        """Генерация API ключа"""
        return f"{prefix}_{secrets.token_hex(32)}"
        
    @staticmethod
    def generate_token(length: int = 64) -> str:
        """Генерация токена"""
        return secrets.token_urlsafe(length)
        
    @staticmethod
    def generate_connection_string(db_type: str, host: str, port: int, 
                                  database: str, username: str, password: str) -> str:
        """Генерация строки подключения"""
        return f"{db_type}://{username}:{password}@{host}:{port}/{database}"


class SecretStore:
    """Хранилище секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        self.path_index: Dict[str, str] = {}  # path -> secret_id
        self.encryption = EncryptionEngine()
        
    def store(self, secret: Secret, value: str) -> SecretVersion:
        """Сохранение секрета"""
        encrypted = self.encryption.encrypt(value)
        
        version = SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version_number=secret.current_version + 1,
            encrypted_value=encrypted,
            created_at=datetime.now()
        )
        
        secret.versions.append(version)
        secret.current_version = version.version_number
        secret.updated_at = datetime.now()
        
        # Trim old versions
        if len(secret.versions) > secret.max_versions:
            secret.versions = secret.versions[-secret.max_versions:]
            
        self.secrets[secret.secret_id] = secret
        self.path_index[secret.path] = secret.secret_id
        
        return version
        
    def retrieve(self, secret_id: str, version: int = 0) -> Optional[str]:
        """Получение секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return None
            
        # Get version
        target_version = version or secret.current_version
        
        for ver in secret.versions:
            if ver.version_number == target_version:
                secret.access_count += 1
                secret.last_accessed = datetime.now()
                return self.encryption.decrypt(ver.encrypted_value)
                
        return None
        
    def get_by_path(self, path: str) -> Optional[Secret]:
        """Получение по пути"""
        secret_id = self.path_index.get(path)
        if secret_id:
            return self.secrets.get(secret_id)
        return None
        
    def delete(self, secret_id: str):
        """Удаление секрета"""
        if secret_id in self.secrets:
            secret = self.secrets[secret_id]
            if secret.path in self.path_index:
                del self.path_index[secret.path]
            del self.secrets[secret_id]
            
    def list_secrets(self, path_prefix: str = "") -> List[Secret]:
        """Список секретов"""
        if not path_prefix:
            return list(self.secrets.values())
        return [s for s in self.secrets.values() if s.path.startswith(path_prefix)]


class AccessController:
    """Контроллер доступа"""
    
    def __init__(self):
        self.policies: Dict[str, AccessPolicy] = {}
        
    def add_policy(self, policy: AccessPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def check_access(self, path: str, actor_id: str, actor_roles: List[str],
                    permission: AccessLevel, source_ip: str = "") -> bool:
        """Проверка доступа"""
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            # Check path match
            if not self._path_matches(path, policy.path_pattern):
                continue
                
            # Check actor
            if actor_id in policy.allowed_services:
                if self._check_conditions(policy, source_ip):
                    if permission in policy.permissions:
                        return True
                        
            # Check roles
            for role in actor_roles:
                if role in policy.allowed_roles:
                    if self._check_conditions(policy, source_ip):
                        if permission in policy.permissions:
                            return True
                            
        return False
        
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Проверка соответствия пути"""
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return path.startswith(prefix)
        return path == pattern
        
    def _check_conditions(self, policy: AccessPolicy, source_ip: str) -> bool:
        """Проверка условий"""
        # IP whitelist
        if policy.ip_whitelist and source_ip:
            if source_ip not in policy.ip_whitelist:
                return False
                
        # Time restrictions
        if policy.time_restrictions:
            now = datetime.now()
            start = int(policy.time_restrictions.get("start_hour", 0))
            end = int(policy.time_restrictions.get("end_hour", 24))
            if not (start <= now.hour < end):
                return False
                
        return True


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        
    def log(self, action: AuditAction, secret_path: str, actor_id: str,
           success: bool = True, **kwargs) -> AuditEntry:
        """Логирование"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            action=action,
            secret_path=secret_path,
            actor_id=actor_id,
            success=success,
            **kwargs
        )
        self.entries.append(entry)
        return entry
        
    def get_entries(self, path: str = "", actor: str = "", 
                   limit: int = 100) -> List[AuditEntry]:
        """Получение записей"""
        results = self.entries
        
        if path:
            results = [e for e in results if e.secret_path.startswith(path)]
        if actor:
            results = [e for e in results if e.actor_id == actor]
            
        return sorted(results, key=lambda e: e.timestamp, reverse=True)[:limit]


class RotationManager:
    """Менеджер ротации"""
    
    def __init__(self, store: SecretStore, generator: SecretGenerator):
        self.store = store
        self.generator = generator
        self.rotation_callbacks: Dict[SecretType, Callable] = {}
        
    def register_rotation_handler(self, secret_type: SecretType, callback: Callable):
        """Регистрация обработчика ротации"""
        self.rotation_callbacks[secret_type] = callback
        
    async def rotate_secret(self, secret_id: str) -> Optional[str]:
        """Ротация секрета"""
        secret = self.store.secrets.get(secret_id)
        if not secret:
            return None
            
        # Generate new value
        new_value = self._generate_value(secret.secret_type)
        
        # Mark old version as rotated
        for version in secret.versions:
            if version.version_number == secret.current_version:
                version.status = SecretStatus.ROTATED
                
        # Store new version
        self.store.store(secret, new_value)
        
        # Update rotation timestamps
        secret.last_rotated = datetime.now()
        if secret.rotation_enabled:
            secret.next_rotation = datetime.now() + timedelta(days=secret.rotation_interval_days)
            
        # Call rotation callback
        if secret.secret_type in self.rotation_callbacks:
            await self.rotation_callbacks[secret.secret_type](secret, new_value)
            
        return new_value
        
    def _generate_value(self, secret_type: SecretType) -> str:
        """Генерация значения"""
        if secret_type == SecretType.PASSWORD:
            return self.generator.generate_password()
        elif secret_type == SecretType.API_KEY:
            return self.generator.generate_api_key()
        elif secret_type == SecretType.TOKEN:
            return self.generator.generate_token()
        else:
            return self.generator.generate_password(48)
            
    async def check_and_rotate(self) -> List[str]:
        """Проверка и автоматическая ротация"""
        rotated = []
        now = datetime.now()
        
        for secret in self.store.secrets.values():
            if not secret.rotation_enabled:
                continue
            if secret.next_rotation and now >= secret.next_rotation:
                await self.rotate_secret(secret.secret_id)
                rotated.append(secret.name)
                
        return rotated


class DynamicSecretManager:
    """Менеджер динамических секретов"""
    
    def __init__(self):
        self.configs: Dict[str, DynamicSecretConfig] = {}
        self.leases: Dict[str, SecretLease] = {}
        
    def register_backend(self, config: DynamicSecretConfig):
        """Регистрация бэкенда"""
        self.configs[config.config_id] = config
        
    async def generate_secret(self, config_id: str, client_id: str, 
                             ttl_sec: int = 0) -> Optional[SecretLease]:
        """Генерация динамического секрета"""
        config = self.configs.get(config_id)
        if not config:
            return None
            
        ttl = ttl_sec or config.default_ttl_sec
        ttl = min(ttl, config.max_ttl_sec)
        
        # Generate credentials based on backend
        secret_value = self._generate_credentials(config)
        
        lease = SecretLease(
            lease_id=f"lease_{uuid.uuid4().hex[:12]}",
            config_id=config_id,
            secret_value=secret_value,
            expires_at=datetime.now() + timedelta(seconds=ttl),
            client_id=client_id
        )
        
        self.leases[lease.lease_id] = lease
        return lease
        
    def _generate_credentials(self, config: DynamicSecretConfig) -> Dict[str, str]:
        """Генерация учётных данных"""
        if config.backend_type == "database":
            username = f"app_{secrets.token_hex(4)}"
            password = SecretGenerator.generate_password(24)
            return {
                "username": username,
                "password": password,
                "host": config.backend_config.get("host", "localhost"),
                "database": config.backend_config.get("database", "default")
            }
        elif config.backend_type == "aws":
            return {
                "access_key": f"AKIA{secrets.token_hex(8).upper()}",
                "secret_key": secrets.token_hex(20)
            }
        else:
            return {"token": secrets.token_hex(32)}
            
    async def revoke_lease(self, lease_id: str) -> bool:
        """Отзыв аренды"""
        if lease_id in self.leases:
            # In production, cleanup actual credentials
            del self.leases[lease_id]
            return True
        return False
        
    async def renew_lease(self, lease_id: str, ttl_sec: int = 0) -> Optional[SecretLease]:
        """Обновление аренды"""
        lease = self.leases.get(lease_id)
        if not lease or not lease.renewable:
            return None
            
        config = self.configs.get(lease.config_id)
        if not config:
            return None
            
        ttl = ttl_sec or config.default_ttl_sec
        ttl = min(ttl, config.max_ttl_sec)
        
        lease.expires_at = datetime.now() + timedelta(seconds=ttl)
        lease.renewals_count += 1
        
        return lease


class SecretsManagementPlatform:
    """Платформа управления секретами"""
    
    def __init__(self):
        self.store = SecretStore()
        self.access_control = AccessController()
        self.audit = AuditLogger()
        self.generator = SecretGenerator()
        self.rotation = RotationManager(self.store, self.generator)
        self.dynamic_secrets = DynamicSecretManager()
        
    def create_secret(self, path: str, value: str, secret_type: SecretType = SecretType.GENERIC,
                     actor_id: str = "system", **kwargs) -> Secret:
        """Создание секрета"""
        secret = Secret(
            secret_id=f"sec_{uuid.uuid4().hex[:8]}",
            name=path.split("/")[-1],
            path=path,
            secret_type=secret_type,
            **kwargs
        )
        
        self.store.store(secret, value)
        
        self.audit.log(AuditAction.CREATE, path, actor_id)
        
        return secret
        
    def get_secret(self, path: str, actor_id: str, actor_roles: List[str] = None,
                  version: int = 0, source_ip: str = "") -> Optional[str]:
        """Получение секрета"""
        actor_roles = actor_roles or []
        
        # Check access
        if not self.access_control.check_access(path, actor_id, actor_roles, AccessLevel.READ, source_ip):
            self.audit.log(AuditAction.ACCESS_DENIED, path, actor_id, success=False)
            return None
            
        secret = self.store.get_by_path(path)
        if not secret:
            return None
            
        value = self.store.retrieve(secret.secret_id, version)
        
        self.audit.log(AuditAction.READ, path, actor_id, secret_version=version or secret.current_version)
        
        return value
        
    async def rotate_secret(self, path: str, actor_id: str) -> Optional[str]:
        """Ротация секрета"""
        secret = self.store.get_by_path(path)
        if not secret:
            return None
            
        new_value = await self.rotation.rotate_secret(secret.secret_id)
        
        self.audit.log(AuditAction.ROTATE, path, actor_id)
        
        return new_value
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_versions = sum(len(s.versions) for s in self.store.secrets.values())
        
        return {
            "total_secrets": len(self.store.secrets),
            "total_versions": total_versions,
            "policies": len(self.access_control.policies),
            "audit_entries": len(self.audit.entries),
            "dynamic_configs": len(self.dynamic_secrets.configs),
            "active_leases": len(self.dynamic_secrets.leases)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 170: Secrets Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = SecretsManagementPlatform()
        print("✓ Secrets Management Platform created")
        
        # Setup access policies
        print("\n🔐 Configuring Access Policies...")
        
        platform.access_control.add_policy(AccessPolicy(
            policy_id="policy_prod",
            name="Production Access",
            path_pattern="/production/*",
            allowed_services=["api-service", "backend-service"],
            allowed_roles=["admin", "sre"],
            permissions=[AccessLevel.READ, AccessLevel.ROTATE]
        ))
        
        platform.access_control.add_policy(AccessPolicy(
            policy_id="policy_dev",
            name="Development Access",
            path_pattern="/development/*",
            allowed_roles=["developer", "admin"],
            permissions=[AccessLevel.READ, AccessLevel.WRITE]
        ))
        
        platform.access_control.add_policy(AccessPolicy(
            policy_id="policy_admin",
            name="Admin Full Access",
            path_pattern="*",
            allowed_roles=["admin"],
            permissions=[AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN, AccessLevel.ROTATE]
        ))
        
        print(f"  ✓ {len(platform.access_control.policies)} policies configured")
        
        # Create secrets
        print("\n🔑 Creating Secrets...")
        
        # Database passwords
        db_password = platform.create_secret(
            path="/production/database/master_password",
            value=SecretGenerator.generate_password(32),
            secret_type=SecretType.PASSWORD,
            actor_id="admin",
            description="Production database master password",
            rotation_enabled=True,
            rotation_interval_days=30
        )
        print(f"  ✓ {db_password.path}")
        
        # API keys
        api_key = platform.create_secret(
            path="/production/services/payment_api_key",
            value=SecretGenerator.generate_api_key("pk"),
            secret_type=SecretType.API_KEY,
            actor_id="admin",
            description="Payment service API key"
        )
        print(f"  ✓ {api_key.path}")
        
        # JWT secret
        jwt_secret = platform.create_secret(
            path="/production/auth/jwt_secret",
            value=SecretGenerator.generate_token(64),
            secret_type=SecretType.TOKEN,
            actor_id="admin",
            description="JWT signing secret"
        )
        print(f"  ✓ {jwt_secret.path}")
        
        # Connection string
        conn_str = platform.create_secret(
            path="/production/database/connection_string",
            value=SecretGenerator.generate_connection_string(
                "postgresql", "db.example.com", 5432,
                "production", "app_user", "secret_password"
            ),
            secret_type=SecretType.CONNECTION_STRING,
            actor_id="admin",
            description="Production database connection string"
        )
        print(f"  ✓ {conn_str.path}")
        
        # Development secrets
        dev_secret = platform.create_secret(
            path="/development/test/api_key",
            value="dev_test_key_12345",
            secret_type=SecretType.API_KEY,
            actor_id="developer"
        )
        print(f"  ✓ {dev_secret.path}")
        
        # List secrets
        print("\n📋 Stored Secrets:")
        
        secrets_list = platform.store.list_secrets()
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Path                                      │ Type        │ Version │ Status     │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for sec in secrets_list:
            path = sec.path[:40].ljust(40)
            stype = sec.secret_type.value[:11].ljust(11)
            current_status = sec.versions[-1].status.value if sec.versions else "none"
            print(f"  │ {path} │ {stype} │ v{sec.current_version:>5} │ {current_status:>10} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Access secrets
        print("\n🔓 Accessing Secrets...")
        
        # Successful access
        value = platform.get_secret(
            "/production/database/master_password",
            actor_id="api-service"
        )
        if value:
            masked = value[:4] + "*" * (len(value) - 4)
            print(f"  ✓ api-service accessed database password: {masked}")
            
        # Unauthorized access
        value = platform.get_secret(
            "/production/database/master_password",
            actor_id="unknown-service"
        )
        if not value:
            print(f"  ✗ unknown-service denied access to database password")
            
        # Developer access to dev secrets
        value = platform.get_secret(
            "/development/test/api_key",
            actor_id="dev-user",
            actor_roles=["developer"]
        )
        if value:
            print(f"  ✓ developer accessed dev API key: {value}")
            
        # Secret rotation
        print("\n🔄 Rotating Secrets...")
        
        old_password = platform.store.retrieve(db_password.secret_id)
        new_password = await platform.rotate_secret(
            "/production/database/master_password",
            actor_id="admin"
        )
        
        if new_password:
            print(f"  ✓ Database password rotated")
            print(f"    Old: {old_password[:8]}... → New: {new_password[:8]}...")
            
        # Version history
        print("\n📜 Secret Version History:")
        
        db_secret = platform.store.get_by_path("/production/database/master_password")
        
        print(f"\n  Secret: {db_secret.path}")
        print(f"  Current version: {db_secret.current_version}")
        print(f"  Total versions: {len(db_secret.versions)}")
        
        print("\n  ┌────────────────────────────────────────────────────────────────┐")
        print("  │ Version │ Status     │ Created At           │")
        print("  ├────────────────────────────────────────────────────────────────┤")
        
        for ver in db_secret.versions:
            created = ver.created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  │ v{ver.version_number:>5} │ {ver.status.value:>10} │ {created:>20} │")
            
        print("  └────────────────────────────────────────────────────────────────┘")
        
        # Dynamic secrets
        print("\n⚡ Dynamic Secrets...")
        
        # Register database backend
        platform.dynamic_secrets.register_backend(DynamicSecretConfig(
            config_id="db_dynamic",
            name="Database Dynamic Credentials",
            backend_type="database",
            backend_config={
                "host": "db.example.com",
                "database": "production"
            },
            default_ttl_sec=3600,
            max_ttl_sec=86400
        ))
        
        # Generate dynamic credentials
        lease = await platform.dynamic_secrets.generate_secret(
            "db_dynamic",
            client_id="worker-1",
            ttl_sec=1800
        )
        
        if lease:
            print(f"\n  ✓ Generated dynamic database credentials")
            print(f"    Lease ID: {lease.lease_id}")
            print(f"    Username: {lease.secret_value.get('username')}")
            print(f"    Password: {lease.secret_value.get('password')[:8]}...")
            print(f"    Expires: {lease.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        # Renew lease
        renewed = await platform.dynamic_secrets.renew_lease(lease.lease_id, 3600)
        if renewed:
            print(f"  ✓ Lease renewed until {renewed.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        # Audit log
        print("\n📝 Audit Log:")
        
        entries = platform.audit.get_entries(limit=10)
        
        print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Time        │ Action          │ Path                              │ Actor        │ Status │")
        print("  ├──────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for entry in entries[:8]:
            time_str = entry.timestamp.strftime("%H:%M:%S")
            action = entry.action.value[:15].ljust(15)
            path = entry.secret_path[:33].ljust(33)
            actor = entry.actor_id[:12].ljust(12)
            status = "✓" if entry.success else "✗"
            print(f"  │ {time_str} │ {action} │ {path} │ {actor} │ {status:>6} │")
            
        print("  └──────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Secrets: {stats['total_secrets']}")
        print(f"  Total Versions: {stats['total_versions']}")
        print(f"  Access Policies: {stats['policies']}")
        print(f"  Audit Entries: {stats['audit_entries']}")
        print(f"  Dynamic Configs: {stats['dynamic_configs']}")
        print(f"  Active Leases: {stats['active_leases']}")
        
        # Secret types distribution
        print("\n  Secret Types Distribution:")
        
        type_counts = defaultdict(int)
        for sec in platform.store.secrets.values():
            type_counts[sec.secret_type.name] += 1
            
        for stype, count in sorted(type_counts.items()):
            bar = "█" * count * 3
            print(f"    {stype:18}: {bar} {count}")
            
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                  Secrets Management Dashboard                      │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Secrets:               {stats['total_secrets']:>10}                       │")
        print(f"│ Secret Versions:             {stats['total_versions']:>10}                       │")
        print(f"│ Access Policies:             {stats['policies']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Audit Entries:               {stats['audit_entries']:>10}                       │")
        print(f"│ Dynamic Secret Configs:      {stats['dynamic_configs']:>10}                       │")
        print(f"│ Active Leases:               {stats['active_leases']:>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Secrets Management Platform initialized!")
    print("=" * 60)
