#!/usr/bin/env python3
"""
Server Init - Iteration 337: Secrets Manager Platform
Платформа управления секретами

Функционал:
- Secret Storage - хранение секретов
- Encryption - шифрование
- Access Control - контроль доступа
- Rotation - ротация секретов
- Versioning - версионирование
- Audit Logging - аудит
- Dynamic Secrets - динамические секреты
- Secret Injection - инъекция секретов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib
import base64


class SecretType(Enum):
    """Тип секрета"""
    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    TOKEN = "token"
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    TLS_CERTIFICATE = "tls_certificate"


class EncryptionAlgorithm(Enum):
    """Алгоритм шифрования"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"


class RotationPolicy(Enum):
    """Политика ротации"""
    MANUAL = "manual"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"
    EVENT_BASED = "event_based"


class AccessLevel(Enum):
    """Уровень доступа"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class SecretStatus(Enum):
    """Статус секрета"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"
    ROTATING = "rotating"


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
class SecretMetadata:
    """Метаданные секрета"""
    secret_id: str
    name: str
    
    # Type
    secret_type: SecretType = SecretType.PASSWORD
    
    # Organization
    path: str = ""  # secrets/prod/database/mysql
    tags: List[str] = field(default_factory=list)
    description: str = ""
    
    # Encryption
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_id: str = ""
    
    # Rotation
    rotation_policy: RotationPolicy = RotationPolicy.MANUAL
    rotation_interval_days: int = 90
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Versioning
    current_version: int = 1
    max_versions: int = 10
    
    # Status
    status: SecretStatus = SecretStatus.ACTIVE
    
    # Expiration
    expires_at: Optional[datetime] = None
    
    # Ownership
    owner_id: str = ""
    created_by: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecretVersion:
    """Версия секрета"""
    version_id: str
    secret_id: str
    version_number: int
    
    # Encrypted value
    encrypted_value: str = ""
    checksum: str = ""
    
    # Encryption
    encryption_key_id: str = ""
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    
    # Status
    is_current: bool = True
    is_deleted: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecretPolicy:
    """Политика доступа к секрету"""
    policy_id: str
    name: str
    
    # Scope
    secret_paths: List[str] = field(default_factory=list)  # wildcards supported
    secret_types: List[SecretType] = field(default_factory=list)
    
    # Permissions
    allowed_actions: List[AccessLevel] = field(default_factory=list)
    
    # Principals
    principals: List[str] = field(default_factory=list)  # users, roles, services
    
    # Conditions
    allowed_ips: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    require_mfa: bool = False
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecretAccessRequest:
    """Запрос доступа к секрету"""
    request_id: str
    
    # Requester
    principal_id: str = ""
    principal_type: str = ""  # user, service, application
    
    # Target
    secret_id: str = ""
    secret_path: str = ""
    
    # Action
    action: AccessLevel = AccessLevel.READ
    
    # Context
    source_ip: str = ""
    user_agent: str = ""
    
    # Result
    granted: bool = False
    policy_id: str = ""
    denial_reason: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)


@dataclass
class EncryptionKey:
    """Ключ шифрования"""
    key_id: str
    name: str
    
    # Algorithm
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    
    # Key material (simulated)
    key_version: int = 1
    
    # Status
    is_active: bool = True
    is_primary: bool = False
    
    # Rotation
    rotated_at: Optional[datetime] = None
    
    # Usage
    usage_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DynamicSecretConfig:
    """Конфигурация динамического секрета"""
    config_id: str
    name: str
    
    # Type
    backend_type: str = "database"  # database, aws, gcp, azure, consul
    
    # Backend connection
    connection_string: str = ""
    credentials_id: str = ""
    
    # Generation
    role_name: str = ""
    ttl_seconds: int = 3600  # 1 hour
    max_ttl_seconds: int = 86400  # 24 hours
    
    # Template
    creation_statements: List[str] = field(default_factory=list)
    revocation_statements: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Stats
    secrets_generated: int = 0
    last_generated: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DynamicSecret:
    """Динамический секрет"""
    lease_id: str
    
    # Source
    config_id: str = ""
    
    # Credentials
    username: str = ""
    password: str = ""
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    # Lease
    ttl_seconds: int = 3600
    expires_at: Optional[datetime] = None
    is_revoked: bool = False
    is_renewable: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecretInjection:
    """Конфигурация инъекции секрета"""
    injection_id: str
    name: str
    
    # Target
    target_type: str = "kubernetes"  # kubernetes, docker, env, file
    target_namespace: str = ""
    target_name: str = ""
    
    # Secrets mapping
    secret_mappings: Dict[str, str] = field(default_factory=dict)  # env_var -> secret_path
    
    # Format
    output_format: str = "env"  # env, json, yaml, file
    
    # Status
    is_enabled: bool = True
    last_synced: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditLog:
    """Запись аудита"""
    log_id: str
    
    # Action
    action: AuditAction = AuditAction.READ
    
    # Target
    secret_id: str = ""
    secret_path: str = ""
    
    # Actor
    principal_id: str = ""
    principal_type: str = ""
    
    # Context
    source_ip: str = ""
    user_agent: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RotationJob:
    """Задание на ротацию"""
    job_id: str
    
    # Target
    secret_id: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    
    # Result
    old_version: int = 0
    new_version: int = 0
    
    # Error
    error_message: str = ""
    
    # Timestamps
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SecretsManager:
    """Менеджер секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, SecretMetadata] = {}
        self.versions: Dict[str, List[SecretVersion]] = {}
        self.policies: Dict[str, SecretPolicy] = {}
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.dynamic_configs: Dict[str, DynamicSecretConfig] = {}
        self.dynamic_secrets: Dict[str, DynamicSecret] = {}
        self.injections: Dict[str, SecretInjection] = {}
        self.audit_logs: List[AuditLog] = []
        self.rotation_jobs: Dict[str, RotationJob] = {}
        
        # Initialize master encryption key
        self._init_master_key()
        
    def _init_master_key(self):
        """Инициализация мастер-ключа"""
        master_key = EncryptionKey(
            key_id="mk_primary",
            name="Master Encryption Key",
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            is_active=True,
            is_primary=True
        )
        self.encryption_keys[master_key.key_id] = master_key
        
    def _encrypt_value(self, value: str, key_id: str) -> str:
        """Симуляция шифрования"""
        key = self.encryption_keys.get(key_id)
        if key:
            key.usage_count += 1
        # Simulate encryption
        encoded = base64.b64encode(value.encode()).decode()
        return f"ENC[{key_id}:{encoded}]"
        
    def _decrypt_value(self, encrypted: str, key_id: str) -> str:
        """Симуляция дешифрования"""
        # Simulate decryption
        if encrypted.startswith("ENC["):
            parts = encrypted[4:-1].split(":", 1)
            if len(parts) == 2:
                return base64.b64decode(parts[1]).decode()
        return encrypted
        
    def _generate_checksum(self, value: str) -> str:
        """Генерация контрольной суммы"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
        
    async def create_secret(self, name: str,
                           value: str,
                           secret_type: SecretType,
                           path: str,
                           owner_id: str,
                           description: str = "",
                           tags: List[str] = None,
                           rotation_policy: RotationPolicy = RotationPolicy.MANUAL,
                           rotation_interval_days: int = 90,
                           expires_at: Optional[datetime] = None) -> SecretMetadata:
        """Создание секрета"""
        secret = SecretMetadata(
            secret_id=f"sec_{uuid.uuid4().hex[:12]}",
            name=name,
            secret_type=secret_type,
            path=path,
            description=description,
            tags=tags or [],
            encryption_algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id="mk_primary",
            rotation_policy=rotation_policy,
            rotation_interval_days=rotation_interval_days,
            owner_id=owner_id,
            created_by=owner_id,
            expires_at=expires_at
        )
        
        # Calculate next rotation
        if rotation_policy == RotationPolicy.TIME_BASED:
            secret.next_rotation = datetime.now() + timedelta(days=rotation_interval_days)
            
        # Create initial version
        version = SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            secret_id=secret.secret_id,
            version_number=1,
            encrypted_value=self._encrypt_value(value, "mk_primary"),
            checksum=self._generate_checksum(value),
            encryption_key_id="mk_primary"
        )
        
        self.secrets[secret.secret_id] = secret
        self.versions[secret.secret_id] = [version]
        
        # Audit log
        await self._log_audit(AuditAction.CREATE, secret.secret_id, path, owner_id)
        
        return secret
        
    async def get_secret_value(self, secret_id: str,
                              principal_id: str,
                              source_ip: str = "",
                              version: int = None) -> Optional[str]:
        """Получение значения секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return None
            
        # Check access
        if not await self._check_access(secret_id, secret.path, principal_id, AccessLevel.READ, source_ip):
            await self._log_audit(AuditAction.ACCESS_DENIED, secret_id, secret.path, principal_id)
            return None
            
        # Get version
        versions = self.versions.get(secret_id, [])
        if not versions:
            return None
            
        if version:
            target_version = next((v for v in versions if v.version_number == version), None)
        else:
            target_version = next((v for v in versions if v.is_current), None)
            
        if not target_version:
            return None
            
        # Decrypt
        value = self._decrypt_value(target_version.encrypted_value, target_version.encryption_key_id)
        
        # Audit log
        await self._log_audit(AuditAction.READ, secret_id, secret.path, principal_id)
        
        return value
        
    async def update_secret(self, secret_id: str,
                           new_value: str,
                           principal_id: str) -> bool:
        """Обновление секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return False
            
        # Check access
        if not await self._check_access(secret_id, secret.path, principal_id, AccessLevel.WRITE):
            await self._log_audit(AuditAction.ACCESS_DENIED, secret_id, secret.path, principal_id)
            return False
            
        # Create new version
        versions = self.versions.get(secret_id, [])
        
        # Mark old current as not current
        for v in versions:
            v.is_current = False
            
        new_version_num = secret.current_version + 1
        
        new_version = SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            secret_id=secret_id,
            version_number=new_version_num,
            encrypted_value=self._encrypt_value(new_value, "mk_primary"),
            checksum=self._generate_checksum(new_value),
            encryption_key_id="mk_primary",
            is_current=True
        )
        
        versions.append(new_version)
        
        # Trim old versions
        if len(versions) > secret.max_versions:
            versions = sorted(versions, key=lambda v: v.version_number, reverse=True)[:secret.max_versions]
            self.versions[secret_id] = versions
            
        secret.current_version = new_version_num
        secret.updated_at = datetime.now()
        
        # Audit log
        await self._log_audit(AuditAction.UPDATE, secret_id, secret.path, principal_id)
        
        return True
        
    async def rotate_secret(self, secret_id: str,
                           new_value: str,
                           principal_id: str) -> Optional[RotationJob]:
        """Ротация секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return None
            
        # Check access
        if not await self._check_access(secret_id, secret.path, principal_id, AccessLevel.ADMIN):
            await self._log_audit(AuditAction.ACCESS_DENIED, secret_id, secret.path, principal_id)
            return None
            
        job = RotationJob(
            job_id=f"rot_{uuid.uuid4().hex[:8]}",
            secret_id=secret_id,
            old_version=secret.current_version,
            status="in_progress",
            started_at=datetime.now()
        )
        
        secret.status = SecretStatus.ROTATING
        
        # Update secret value
        success = await self.update_secret(secret_id, new_value, principal_id)
        
        if success:
            job.status = "completed"
            job.new_version = secret.current_version
            job.completed_at = datetime.now()
            
            secret.status = SecretStatus.ACTIVE
            secret.last_rotated = datetime.now()
            
            if secret.rotation_policy == RotationPolicy.TIME_BASED:
                secret.next_rotation = datetime.now() + timedelta(days=secret.rotation_interval_days)
                
            # Audit log
            await self._log_audit(AuditAction.ROTATE, secret_id, secret.path, principal_id)
        else:
            job.status = "failed"
            job.error_message = "Failed to update secret"
            secret.status = SecretStatus.ACTIVE
            
        self.rotation_jobs[job.job_id] = job
        return job
        
    async def revoke_secret(self, secret_id: str, principal_id: str) -> bool:
        """Отзыв секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return False
            
        # Check access
        if not await self._check_access(secret_id, secret.path, principal_id, AccessLevel.ADMIN):
            await self._log_audit(AuditAction.ACCESS_DENIED, secret_id, secret.path, principal_id)
            return False
            
        secret.status = SecretStatus.REVOKED
        secret.updated_at = datetime.now()
        
        # Audit log
        await self._log_audit(AuditAction.REVOKE, secret_id, secret.path, principal_id)
        
        return True
        
    async def delete_secret(self, secret_id: str, principal_id: str) -> bool:
        """Удаление секрета"""
        secret = self.secrets.get(secret_id)
        if not secret:
            return False
            
        # Check access
        if not await self._check_access(secret_id, secret.path, principal_id, AccessLevel.DELETE):
            await self._log_audit(AuditAction.ACCESS_DENIED, secret_id, secret.path, principal_id)
            return False
            
        # Soft delete versions
        versions = self.versions.get(secret_id, [])
        for v in versions:
            v.is_deleted = True
            
        # Remove from active secrets
        del self.secrets[secret_id]
        
        # Audit log
        await self._log_audit(AuditAction.DELETE, secret_id, secret.path, principal_id)
        
        return True
        
    async def create_policy(self, name: str,
                           secret_paths: List[str],
                           allowed_actions: List[AccessLevel],
                           principals: List[str],
                           require_mfa: bool = False,
                           allowed_ips: List[str] = None) -> SecretPolicy:
        """Создание политики доступа"""
        policy = SecretPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            secret_paths=secret_paths,
            allowed_actions=allowed_actions,
            principals=principals,
            require_mfa=require_mfa,
            allowed_ips=allowed_ips or []
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def _check_access(self, secret_id: str,
                           secret_path: str,
                           principal_id: str,
                           action: AccessLevel,
                           source_ip: str = "") -> bool:
        """Проверка доступа"""
        for policy in self.policies.values():
            if not policy.is_enabled:
                continue
                
            # Check principal
            if principal_id not in policy.principals and "*" not in policy.principals:
                continue
                
            # Check path
            path_match = False
            for pattern in policy.secret_paths:
                if pattern == "*" or pattern == secret_path:
                    path_match = True
                    break
                if pattern.endswith("/*") and secret_path.startswith(pattern[:-1]):
                    path_match = True
                    break
                    
            if not path_match:
                continue
                
            # Check action
            if action not in policy.allowed_actions and AccessLevel.ADMIN not in policy.allowed_actions:
                continue
                
            # Check IP
            if policy.allowed_ips and source_ip and source_ip not in policy.allowed_ips:
                continue
                
            return True
            
        return False
        
    async def configure_dynamic_secret(self, name: str,
                                      backend_type: str,
                                      connection_string: str,
                                      role_name: str,
                                      ttl_seconds: int = 3600,
                                      creation_statements: List[str] = None,
                                      revocation_statements: List[str] = None) -> DynamicSecretConfig:
        """Настройка динамического секрета"""
        config = DynamicSecretConfig(
            config_id=f"dsc_{uuid.uuid4().hex[:8]}",
            name=name,
            backend_type=backend_type,
            connection_string=connection_string,
            role_name=role_name,
            ttl_seconds=ttl_seconds,
            creation_statements=creation_statements or [],
            revocation_statements=revocation_statements or []
        )
        
        self.dynamic_configs[config.config_id] = config
        return config
        
    async def generate_dynamic_secret(self, config_id: str,
                                     principal_id: str) -> Optional[DynamicSecret]:
        """Генерация динамического секрета"""
        config = self.dynamic_configs.get(config_id)
        if not config or not config.is_enabled:
            return None
            
        # Generate credentials
        username = f"dynamic_{config.role_name}_{uuid.uuid4().hex[:8]}"
        password = uuid.uuid4().hex + uuid.uuid4().hex[:8].upper()
        
        lease = DynamicSecret(
            lease_id=f"lease_{uuid.uuid4().hex[:12]}",
            config_id=config_id,
            username=username,
            password=password,
            ttl_seconds=config.ttl_seconds,
            expires_at=datetime.now() + timedelta(seconds=config.ttl_seconds)
        )
        
        config.secrets_generated += 1
        config.last_generated = datetime.now()
        
        self.dynamic_secrets[lease.lease_id] = lease
        return lease
        
    async def revoke_dynamic_secret(self, lease_id: str) -> bool:
        """Отзыв динамического секрета"""
        lease = self.dynamic_secrets.get(lease_id)
        if not lease:
            return False
            
        lease.is_revoked = True
        return True
        
    async def renew_dynamic_secret(self, lease_id: str,
                                  ttl_seconds: int = None) -> bool:
        """Продление динамического секрета"""
        lease = self.dynamic_secrets.get(lease_id)
        if not lease or not lease.is_renewable or lease.is_revoked:
            return False
            
        config = self.dynamic_configs.get(lease.config_id)
        if not config:
            return False
            
        new_ttl = ttl_seconds or config.ttl_seconds
        if new_ttl > config.max_ttl_seconds:
            new_ttl = config.max_ttl_seconds
            
        lease.ttl_seconds = new_ttl
        lease.expires_at = datetime.now() + timedelta(seconds=new_ttl)
        
        return True
        
    async def create_injection_config(self, name: str,
                                     target_type: str,
                                     target_namespace: str,
                                     target_name: str,
                                     secret_mappings: Dict[str, str],
                                     output_format: str = "env") -> SecretInjection:
        """Создание конфигурации инъекции секретов"""
        injection = SecretInjection(
            injection_id=f"inj_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            target_namespace=target_namespace,
            target_name=target_name,
            secret_mappings=secret_mappings,
            output_format=output_format
        )
        
        self.injections[injection.injection_id] = injection
        return injection
        
    async def sync_injection(self, injection_id: str,
                            principal_id: str) -> Dict[str, str]:
        """Синхронизация инъекции секретов"""
        injection = self.injections.get(injection_id)
        if not injection or not injection.is_enabled:
            return {}
            
        result = {}
        for env_var, secret_path in injection.secret_mappings.items():
            # Find secret by path
            for secret in self.secrets.values():
                if secret.path == secret_path:
                    value = await self.get_secret_value(secret.secret_id, principal_id)
                    if value:
                        result[env_var] = value
                    break
                    
        injection.last_synced = datetime.now()
        return result
        
    async def _log_audit(self, action: AuditAction,
                        secret_id: str,
                        secret_path: str,
                        principal_id: str,
                        source_ip: str = "",
                        success: bool = True,
                        error: str = "",
                        details: Dict[str, Any] = None):
        """Запись в аудит"""
        log = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:12]}",
            action=action,
            secret_id=secret_id,
            secret_path=secret_path,
            principal_id=principal_id,
            source_ip=source_ip,
            success=success,
            error_message=error,
            details=details or {}
        )
        
        self.audit_logs.append(log)
        
    def get_secrets_needing_rotation(self) -> List[SecretMetadata]:
        """Получение секретов, требующих ротации"""
        result = []
        now = datetime.now()
        
        for secret in self.secrets.values():
            if secret.status != SecretStatus.ACTIVE:
                continue
            if secret.rotation_policy != RotationPolicy.TIME_BASED:
                continue
            if secret.next_rotation and secret.next_rotation <= now:
                result.append(secret)
                
        return result
        
    def get_expiring_secrets(self, days: int = 7) -> List[SecretMetadata]:
        """Получение истекающих секретов"""
        result = []
        threshold = datetime.now() + timedelta(days=days)
        
        for secret in self.secrets.values():
            if secret.status != SecretStatus.ACTIVE:
                continue
            if secret.expires_at and secret.expires_at <= threshold:
                result.append(secret)
                
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_secrets = len(self.secrets)
        active_secrets = sum(1 for s in self.secrets.values() if s.status == SecretStatus.ACTIVE)
        
        # By type
        by_type = {}
        for secret in self.secrets.values():
            t = secret.secret_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        total_policies = len(self.policies)
        enabled_policies = sum(1 for p in self.policies.values() if p.is_enabled)
        
        total_versions = sum(len(v) for v in self.versions.values())
        
        total_dynamic_configs = len(self.dynamic_configs)
        active_leases = sum(1 for l in self.dynamic_secrets.values() 
                          if not l.is_revoked and l.expires_at and l.expires_at > datetime.now())
        
        total_audit_logs = len(self.audit_logs)
        
        needing_rotation = len(self.get_secrets_needing_rotation())
        expiring_soon = len(self.get_expiring_secrets())
        
        return {
            "total_secrets": total_secrets,
            "active_secrets": active_secrets,
            "secrets_by_type": by_type,
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_versions": total_versions,
            "total_dynamic_configs": total_dynamic_configs,
            "active_leases": active_leases,
            "total_audit_logs": total_audit_logs,
            "needing_rotation": needing_rotation,
            "expiring_soon": expiring_soon
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 337: Secrets Manager Platform")
    print("=" * 60)
    
    sm = SecretsManager()
    print("✓ Secrets Manager initialized")
    
    # Create access policies
    print("\n📜 Creating Access Policies...")
    
    policies_data = [
        ("Admin Full Access", ["secrets/*"], [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.DELETE, AccessLevel.ADMIN], ["admin", "security-team"]),
        ("Developer Read", ["secrets/dev/*", "secrets/staging/*"], [AccessLevel.READ], ["developers", "qa-team"]),
        ("Production Read", ["secrets/prod/*"], [AccessLevel.READ], ["prod-apps", "sre-team"]),
        ("Database Admin", ["secrets/*/database/*"], [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN], ["dba-team"]),
        ("Service Account", ["secrets/services/*"], [AccessLevel.READ], ["service-accounts"])
    ]
    
    policies = []
    for name, paths, actions, principals in policies_data:
        policy = await sm.create_policy(name, paths, actions, principals)
        policies.append(policy)
        print(f"  📜 {name}")
        
    # Create secrets
    print("\n🔐 Creating Secrets...")
    
    secrets_data = [
        ("prod-db-password", "SuperSecret123!", SecretType.DATABASE_CREDENTIAL, "secrets/prod/database/mysql", "dba-team", "Production MySQL password", ["production", "database", "mysql"]),
        ("staging-db-password", "StagingPass456!", SecretType.DATABASE_CREDENTIAL, "secrets/staging/database/postgres", "dba-team", "Staging PostgreSQL password", ["staging", "database", "postgres"]),
        ("api-key-stripe", "sk_live_abc123xyz", SecretType.API_KEY, "secrets/prod/api-keys/stripe", "admin", "Stripe production API key", ["production", "payments", "stripe"]),
        ("api-key-sendgrid", "SG.key789", SecretType.API_KEY, "secrets/prod/api-keys/sendgrid", "admin", "SendGrid API key", ["production", "email"]),
        ("jwt-secret", "jwt_secret_key_very_long", SecretType.TOKEN, "secrets/prod/auth/jwt", "security-team", "JWT signing secret", ["production", "auth"]),
        ("oauth-client-secret", "oauth_secret_xyz", SecretType.TOKEN, "secrets/prod/auth/oauth", "security-team", "OAuth client secret", ["production", "auth", "oauth"]),
        ("dev-db-password", "DevPass123", SecretType.DATABASE_CREDENTIAL, "secrets/dev/database/mysql", "developers", "Development database password", ["development", "database"]),
        ("ssh-private-key", "-----BEGIN RSA PRIVATE KEY-----...", SecretType.SSH_KEY, "secrets/prod/ssh/deploy-key", "sre-team", "Deployment SSH key", ["production", "ssh", "deployment"]),
        ("tls-certificate", "-----BEGIN CERTIFICATE-----...", SecretType.TLS_CERTIFICATE, "secrets/prod/tls/wildcard", "sre-team", "Wildcard TLS certificate", ["production", "tls", "ssl"]),
        ("encryption-master-key", "master_encryption_key_data", SecretType.ENCRYPTION_KEY, "secrets/prod/encryption/master", "security-team", "Master encryption key", ["production", "encryption"]),
        ("aws-access-key", "AKIAIOSFODNN7EXAMPLE", SecretType.API_KEY, "secrets/services/aws/access-key", "admin", "AWS access key", ["aws", "cloud"]),
        ("aws-secret-key", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", SecretType.API_KEY, "secrets/services/aws/secret-key", "admin", "AWS secret key", ["aws", "cloud"])
    ]
    
    secrets = []
    for name, value, stype, path, owner, desc, tags in secrets_data:
        secret = await sm.create_secret(
            name, value, stype, path, owner, desc, tags,
            rotation_policy=RotationPolicy.TIME_BASED if "password" in name else RotationPolicy.MANUAL,
            rotation_interval_days=90
        )
        secrets.append(secret)
        print(f"  🔐 {name} ({stype.value})")
        
    # Configure dynamic secrets
    print("\n⚡ Configuring Dynamic Secrets...")
    
    dynamic_configs_data = [
        ("MySQL Dynamic", "database", "mysql://localhost:3306", "app-role", 3600),
        ("PostgreSQL Dynamic", "database", "postgres://localhost:5432", "readonly-role", 7200),
        ("AWS STS", "aws", "sts://aws", "deploy-role", 3600),
        ("MongoDB Dynamic", "database", "mongodb://localhost:27017", "analytics-role", 1800)
    ]
    
    configs = []
    for name, backend, conn, role, ttl in dynamic_configs_data:
        config = await sm.configure_dynamic_secret(
            name, backend, conn, role, ttl,
            creation_statements=["CREATE USER '{{username}}'@'%' IDENTIFIED BY '{{password}}'"],
            revocation_statements=["DROP USER '{{username}}'"]
        )
        configs.append(config)
        print(f"  ⚡ {name} (TTL: {ttl}s)")
        
    # Generate dynamic secrets
    print("\n🔄 Generating Dynamic Secrets...")
    
    leases = []
    for config in configs:
        for i in range(random.randint(2, 4)):
            lease = await sm.generate_dynamic_secret(config.config_id, "admin")
            if lease:
                leases.append(lease)
                
    print(f"  ✓ Generated {len(leases)} dynamic credentials")
    
    # Create injection configs
    print("\n💉 Configuring Secret Injections...")
    
    injections_data = [
        ("Production App", "kubernetes", "production", "app-deployment", {
            "DATABASE_PASSWORD": "secrets/prod/database/mysql",
            "JWT_SECRET": "secrets/prod/auth/jwt",
            "STRIPE_API_KEY": "secrets/prod/api-keys/stripe"
        }),
        ("Staging App", "kubernetes", "staging", "app-deployment", {
            "DATABASE_PASSWORD": "secrets/staging/database/postgres"
        }),
        ("Worker Service", "docker", "default", "worker-container", {
            "AWS_ACCESS_KEY": "secrets/services/aws/access-key",
            "AWS_SECRET_KEY": "secrets/services/aws/secret-key"
        })
    ]
    
    injections = []
    for name, target, ns, tname, mappings in injections_data:
        injection = await sm.create_injection_config(name, target, ns, tname, mappings)
        injections.append(injection)
        print(f"  💉 {name} ({len(mappings)} secrets)")
        
    # Simulate secret access
    print("\n🔑 Simulating Secret Access...")
    
    access_results = []
    access_tests = [
        ("admin", secrets[0].secret_id, True),
        ("developers", secrets[6].secret_id, True),
        ("developers", secrets[0].secret_id, False),  # Should be denied
        ("security-team", secrets[4].secret_id, True),
        ("dba-team", secrets[1].secret_id, True),
        ("service-accounts", secrets[10].secret_id, True)
    ]
    
    for principal, secret_id, expected in access_tests:
        value = await sm.get_secret_value(secret_id, principal)
        success = (value is not None) == expected
        access_results.append((principal, secret_id, value is not None, expected, success))
        
    allowed = sum(1 for r in access_results if r[2])
    denied = sum(1 for r in access_results if not r[2])
    print(f"  ✓ {len(access_results)} access attempts: {allowed} allowed, {denied} denied")
    
    # Rotate a secret
    print("\n🔄 Rotating Secrets...")
    
    rotation_job = await sm.rotate_secret(
        secrets[0].secret_id,
        "NewSuperSecret456!",
        "admin"
    )
    if rotation_job:
        print(f"  ✓ Rotated {secrets[0].name}: v{rotation_job.old_version} → v{rotation_job.new_version}")
        
    # Secrets table
    print("\n🔐 Secrets:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                     │ Type                 │ Path                              │ Version │ Rotation Policy │ Status       │ Owner                                │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for secret in secrets:
        name = secret.name[:24].ljust(24)
        stype = secret.secret_type.value[:20].ljust(20)
        path = secret.path[:33].ljust(33)
        version = f"v{secret.current_version}".ljust(7)
        rotation = secret.rotation_policy.value[:15].ljust(15)
        
        status_icon = {"active": "✓", "expired": "⏰", "revoked": "✗", "rotating": "🔄"}.get(secret.status.value, "?")
        status = f"{status_icon} {secret.status.value}"[:12].ljust(12)
        
        owner = secret.owner_id[:36].ljust(36)
        
        print(f"  │ {name} │ {stype} │ {path} │ {version} │ {rotation} │ {status} │ {owner} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Access Policies
    print("\n📜 Access Policies:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Paths                         │ Actions           │ Principals               │ Status                │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:25].ljust(25)
        paths = ", ".join(policy.secret_paths[:2])[:29].ljust(29)
        actions = ", ".join(a.value for a in policy.allowed_actions[:2])[:17].ljust(17)
        principals = ", ".join(policy.principals[:2])[:24].ljust(24)
        status = "✓ Enabled" if policy.is_enabled else "○ Disabled"
        status = status[:21].ljust(21)
        
        print(f"  │ {name} │ {paths} │ {actions} │ {principals} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Dynamic Secret Configs
    print("\n⚡ Dynamic Secret Configurations:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                   │ Backend     │ Role             │ TTL       │ Generated │ Status                             │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for config in configs:
        name = config.name[:22].ljust(22)
        backend = config.backend_type[:11].ljust(11)
        role = config.role_name[:16].ljust(16)
        ttl = f"{config.ttl_seconds}s".ljust(9)
        generated = str(config.secrets_generated).ljust(9)
        status = "✓ Enabled" if config.is_enabled else "○ Disabled"
        status = status[:35].ljust(35)
        
        print(f"  │ {name} │ {backend} │ {role} │ {ttl} │ {generated} │ {status} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Active Leases
    print("\n🎫 Active Dynamic Leases:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Lease ID              │ Config               │ Username                       │ TTL       │ Expires                │ Status                                │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for lease in leases[:8]:
        lease_id = lease.lease_id[:21].ljust(21)
        
        config = sm.dynamic_configs.get(lease.config_id)
        config_name = config.name if config else "Unknown"
        config_name = config_name[:20].ljust(20)
        
        username = lease.username[:30].ljust(30)
        ttl = f"{lease.ttl_seconds}s".ljust(9)
        expires = lease.expires_at.strftime("%Y-%m-%d %H:%M") if lease.expires_at else "N/A"
        expires = expires[:22].ljust(22)
        
        status_icon = "✓" if not lease.is_revoked else "✗"
        status = f"{status_icon} {'Active' if not lease.is_revoked else 'Revoked'}"[:39].ljust(39)
        
        print(f"  │ {lease_id} │ {config_name} │ {username} │ {ttl} │ {expires} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Secret Injections
    print("\n💉 Secret Injections:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Target Type  │ Namespace   │ Target Name       │ Secrets │ Format │ Status                       │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for injection in injections:
        name = injection.name[:23].ljust(23)
        target = injection.target_type[:12].ljust(12)
        ns = injection.target_namespace[:11].ljust(11)
        tname = injection.target_name[:17].ljust(17)
        secrets_count = str(len(injection.secret_mappings)).ljust(7)
        fmt = injection.output_format[:6].ljust(6)
        status = "✓ Enabled" if injection.is_enabled else "○ Disabled"
        status = status[:28].ljust(28)
        
        print(f"  │ {name} │ {target} │ {ns} │ {tname} │ {secrets_count} │ {fmt} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Audit Logs
    print("\n📋 Recent Audit Logs:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Action          │ Secret Path                         │ Principal           │ Timestamp            │ Status                                                        │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for log in sm.audit_logs[-10:]:
        action = log.action.value[:15].ljust(15)
        path = log.secret_path[:35].ljust(35)
        principal = log.principal_id[:19].ljust(19)
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        
        status_icon = "✓" if log.success else "✗"
        status = f"{status_icon} {'Success' if log.success else log.error_message}"[:61].ljust(61)
        
        print(f"  │ {action} │ {path} │ {principal} │ {timestamp} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = sm.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Secrets: {stats['total_secrets']}")
    print(f"  Active Secrets: {stats['active_secrets']}")
    print(f"  Secret Versions: {stats['total_versions']}")
    print(f"  Access Policies: {stats['enabled_policies']}/{stats['total_policies']} enabled")
    print(f"  Dynamic Configs: {stats['total_dynamic_configs']}")
    print(f"  Active Leases: {stats['active_leases']}")
    print(f"  Audit Logs: {stats['total_audit_logs']}")
    print(f"  Needing Rotation: {stats['needing_rotation']}")
    print(f"  Expiring Soon: {stats['expiring_soon']}")
    
    # Secrets by type
    print("\n  Secrets by Type:")
    for stype, count in stats['secrets_by_type'].items():
        print(f"    {stype}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Secrets Manager Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Secrets:                {stats['total_secrets']:>12}                      │")
    print(f"│ Active Secrets:               {stats['active_secrets']:>12}                      │")
    print(f"│ Secret Versions:              {stats['total_versions']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Dynamic Configs:              {stats['total_dynamic_configs']:>12}                      │")
    print(f"│ Active Leases:                {stats['active_leases']:>12}                      │")
    print(f"│ Audit Entries:                {stats['total_audit_logs']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Secrets Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
