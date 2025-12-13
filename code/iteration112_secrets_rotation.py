#!/usr/bin/env python3
"""
Server Init - Iteration 112: Secrets Rotation Platform
Платформа ротации секретов

Функционал:
- Secret Management - управление секретами
- Automatic Rotation - автоматическая ротация
- Credential Lifecycle - жизненный цикл учётных данных
- Encryption - шифрование
- Audit Trail - аудит доступа
- Integration - интеграция с сервисами
- Expiration Policies - политики истечения
- Emergency Rotation - экстренная ротация
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib
import base64


class SecretType(Enum):
    """Тип секрета"""
    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    DATABASE_CREDENTIAL = "database_credential"
    OAUTH_TOKEN = "oauth_token"
    ENCRYPTION_KEY = "encryption_key"


class RotationStatus(Enum):
    """Статус ротации"""
    ACTIVE = "active"
    ROTATING = "rotating"
    PENDING_VERIFICATION = "pending_verification"
    FAILED = "failed"
    EXPIRED = "expired"


class EncryptionAlgorithm(Enum):
    """Алгоритм шифрования"""
    AES_256_GCM = "aes-256-gcm"
    RSA_4096 = "rsa-4096"
    CHACHA20_POLY1305 = "chacha20-poly1305"


class AccessLevel(Enum):
    """Уровень доступа"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    ROTATE = "rotate"


@dataclass
class SecretVersion:
    """Версия секрета"""
    version_id: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    encrypted_value: str = ""
    active: bool = True
    rotated_by: str = ""
    rotation_reason: str = ""


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    name: str = ""
    
    # Type
    secret_type: SecretType = SecretType.PASSWORD
    
    # Versions
    versions: List[SecretVersion] = field(default_factory=list)
    current_version: Optional[str] = None
    
    # Rotation
    rotation_status: RotationStatus = RotationStatus.ACTIVE
    rotation_interval_days: int = 90
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Encryption
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    
    # Metadata
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    owner: str = ""
    
    # Access
    allowed_services: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RotationPolicy:
    """Политика ротации"""
    policy_id: str
    name: str = ""
    
    # Schedule
    rotation_interval_days: int = 90
    max_age_days: int = 180
    
    # Automation
    auto_rotate: bool = True
    notify_before_days: int = 7
    
    # Actions
    pre_rotation_hook: str = ""
    post_rotation_hook: str = ""
    
    # Targets
    secret_types: List[SecretType] = field(default_factory=list)
    target_secrets: List[str] = field(default_factory=list)


@dataclass
class AccessGrant:
    """Предоставление доступа"""
    grant_id: str
    secret_id: str = ""
    
    # Grantee
    service_id: str = ""
    service_name: str = ""
    
    # Access
    access_level: AccessLevel = AccessLevel.READ
    
    # Time
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Conditions
    ip_whitelist: List[str] = field(default_factory=list)


@dataclass
class AuditEntry:
    """Запись аудита"""
    audit_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Action
    action: str = ""
    secret_id: str = ""
    secret_name: str = ""
    
    # Actor
    actor_id: str = ""
    actor_type: str = ""  # user, service, system
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    success: bool = True


class SecretManager:
    """Менеджер секретов"""
    
    def __init__(self):
        self.secrets: Dict[str, Secret] = {}
        
    def create(self, name: str, secret_type: SecretType,
                value: str, **kwargs) -> Secret:
        """Создание секрета"""
        secret = Secret(
            secret_id=f"sec_{uuid.uuid4().hex[:8]}",
            name=name,
            secret_type=secret_type,
            **kwargs
        )
        
        # Create first version
        version = self._create_version(value)
        secret.versions.append(version)
        secret.current_version = version.version_id
        secret.next_rotation = datetime.now() + timedelta(days=secret.rotation_interval_days)
        
        self.secrets[secret.secret_id] = secret
        return secret
        
    def _create_version(self, value: str, rotated_by: str = "system",
                         reason: str = "Initial creation") -> SecretVersion:
        """Создание версии"""
        # Simulate encryption
        encrypted = base64.b64encode(
            hashlib.sha256(value.encode()).digest()
        ).decode()
        
        return SecretVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            encrypted_value=encrypted,
            rotated_by=rotated_by,
            rotation_reason=reason
        )
        
    def get(self, secret_id: str) -> Optional[Secret]:
        """Получение секрета"""
        return self.secrets.get(secret_id)
        
    def list_expiring(self, days: int = 7) -> List[Secret]:
        """Секреты, истекающие скоро"""
        threshold = datetime.now() + timedelta(days=days)
        return [s for s in self.secrets.values()
               if s.next_rotation and s.next_rotation <= threshold]


class RotationEngine:
    """Движок ротации"""
    
    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager
        self.policies: Dict[str, RotationPolicy] = {}
        self.rotation_hooks: Dict[str, Callable] = {}
        
    def create_policy(self, name: str, **kwargs) -> RotationPolicy:
        """Создание политики"""
        policy = RotationPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    async def rotate(self, secret_id: str, new_value: str = None,
                      reason: str = "Scheduled rotation") -> Dict[str, Any]:
        """Ротация секрета"""
        secret = self.secret_manager.get(secret_id)
        if not secret:
            return {"status": "error", "message": "Secret not found"}
            
        secret.rotation_status = RotationStatus.ROTATING
        
        try:
            # Generate new value if not provided
            if not new_value:
                new_value = self._generate_value(secret.secret_type)
                
            # Create new version
            version = self.secret_manager._create_version(
                new_value, "rotation_engine", reason
            )
            
            # Mark old version as inactive
            for v in secret.versions:
                if v.version_id == secret.current_version:
                    v.active = False
                    break
                    
            # Add new version
            secret.versions.append(version)
            secret.current_version = version.version_id
            secret.last_rotated = datetime.now()
            secret.next_rotation = datetime.now() + timedelta(days=secret.rotation_interval_days)
            
            # Verify rotation (simulate)
            await asyncio.sleep(0.05)
            
            secret.rotation_status = RotationStatus.ACTIVE
            
            return {
                "status": "success",
                "secret_id": secret_id,
                "new_version": version.version_id,
                "next_rotation": secret.next_rotation.isoformat()
            }
            
        except Exception as e:
            secret.rotation_status = RotationStatus.FAILED
            return {"status": "error", "message": str(e)}
            
    def _generate_value(self, secret_type: SecretType) -> str:
        """Генерация значения"""
        if secret_type == SecretType.PASSWORD:
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            return ''.join(random.choice(chars) for _ in range(24))
        elif secret_type == SecretType.API_KEY:
            return f"ak_{uuid.uuid4().hex}"
        else:
            return uuid.uuid4().hex
            
    async def check_and_rotate(self) -> List[Dict[str, Any]]:
        """Проверка и ротация истекающих"""
        results = []
        expiring = self.secret_manager.list_expiring(days=0)
        
        for secret in expiring:
            result = await self.rotate(secret.secret_id, reason="Auto-rotation")
            results.append(result)
            
        return results


class EncryptionService:
    """Сервис шифрования"""
    
    def __init__(self):
        self.master_key = uuid.uuid4().hex
        
    def encrypt(self, value: str, 
                 algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> str:
        """Шифрование"""
        # Simplified simulation
        combined = f"{self.master_key}:{value}:{algorithm.value}"
        return base64.b64encode(
            hashlib.sha256(combined.encode()).digest()
        ).decode()
        
    def rotate_master_key(self) -> str:
        """Ротация мастер-ключа"""
        old_key = self.master_key
        self.master_key = uuid.uuid4().hex
        return self.master_key


class AccessManager:
    """Менеджер доступа"""
    
    def __init__(self):
        self.grants: Dict[str, AccessGrant] = {}
        
    def grant(self, secret_id: str, service_id: str,
               service_name: str, access_level: AccessLevel = AccessLevel.READ,
               **kwargs) -> AccessGrant:
        """Предоставление доступа"""
        grant = AccessGrant(
            grant_id=f"grant_{uuid.uuid4().hex[:8]}",
            secret_id=secret_id,
            service_id=service_id,
            service_name=service_name,
            access_level=access_level,
            **kwargs
        )
        self.grants[grant.grant_id] = grant
        return grant
        
    def revoke(self, grant_id: str) -> bool:
        """Отзыв доступа"""
        if grant_id in self.grants:
            del self.grants[grant_id]
            return True
        return False
        
    def check_access(self, secret_id: str, service_id: str,
                      required_level: AccessLevel = AccessLevel.READ) -> bool:
        """Проверка доступа"""
        for grant in self.grants.values():
            if grant.secret_id == secret_id and grant.service_id == service_id:
                # Check expiration
                if grant.expires_at and grant.expires_at < datetime.now():
                    return False
                    
                # Check level
                levels = [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ROTATE, AccessLevel.ADMIN]
                return levels.index(grant.access_level) >= levels.index(required_level)
                
        return False


class AuditService:
    """Сервис аудита"""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        
    def log(self, action: str, secret_id: str, secret_name: str,
             actor_id: str, actor_type: str = "user",
             success: bool = True, **kwargs) -> AuditEntry:
        """Запись в аудит"""
        entry = AuditEntry(
            audit_id=f"aud_{uuid.uuid4().hex[:8]}",
            action=action,
            secret_id=secret_id,
            secret_name=secret_name,
            actor_id=actor_id,
            actor_type=actor_type,
            success=success,
            details=kwargs.get("details", {})
        )
        self.entries.append(entry)
        return entry
        
    def get_by_secret(self, secret_id: str, limit: int = 100) -> List[AuditEntry]:
        """Записи по секрету"""
        return [e for e in self.entries if e.secret_id == secret_id][-limit:]
        
    def get_recent(self, hours: int = 24) -> List[AuditEntry]:
        """Недавние записи"""
        threshold = datetime.now() - timedelta(hours=hours)
        return [e for e in self.entries if e.timestamp >= threshold]


class SecretsRotationPlatform:
    """Платформа ротации секретов"""
    
    def __init__(self):
        self.secret_manager = SecretManager()
        self.rotation_engine = RotationEngine(self.secret_manager)
        self.encryption = EncryptionService()
        self.access_manager = AccessManager()
        self.audit = AuditService()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        secrets = list(self.secret_manager.secrets.values())
        
        by_type = defaultdict(int)
        for s in secrets:
            by_type[s.secret_type.value] += 1
            
        expiring_soon = len(self.secret_manager.list_expiring(days=7))
        expired = len([s for s in secrets if s.rotation_status == RotationStatus.EXPIRED])
        
        active_grants = len(self.access_manager.grants)
        
        return {
            "total_secrets": len(secrets),
            "secrets_by_type": dict(by_type),
            "expiring_soon": expiring_soon,
            "expired": expired,
            "active_grants": active_grants,
            "policies": len(self.rotation_engine.policies),
            "audit_entries": len(self.audit.entries)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 112: Secrets Rotation Platform")
    print("=" * 60)
    
    async def demo():
        platform = SecretsRotationPlatform()
        print("✓ Secrets Rotation Platform created")
        
        # Create secrets
        print("\n🔐 Creating Secrets...")
        
        secrets_data = [
            ("db/production/password", SecretType.DATABASE_CREDENTIAL, "super_secret_123", 30),
            ("db/staging/password", SecretType.DATABASE_CREDENTIAL, "staging_pass_456", 60),
            ("api/payment-gateway", SecretType.API_KEY, "ak_live_xxxx", 90),
            ("api/analytics", SecretType.API_KEY, "ak_analytics_yyyy", 90),
            ("ssh/deploy-key", SecretType.SSH_KEY, "-----BEGIN RSA-----...", 180),
            ("oauth/google-client", SecretType.OAUTH_TOKEN, "oauth_token_zzzz", 365),
            ("encryption/data-key", SecretType.ENCRYPTION_KEY, "enc_key_master", 365)
        ]
        
        created_secrets = []
        for name, stype, value, rotation_days in secrets_data:
            secret = platform.secret_manager.create(
                name, stype, value,
                rotation_interval_days=rotation_days,
                description=f"Secret for {name}"
            )
            created_secrets.append(secret)
            
            # Log creation
            platform.audit.log(
                "create", secret.secret_id, secret.name,
                "admin", "user", success=True
            )
            
            print(f"  ✓ {name} ({stype.value}) - rotates every {rotation_days} days")
            
        # Create rotation policies
        print("\n📜 Creating Rotation Policies...")
        
        policies_data = [
            ("critical-secrets", 30, True, [SecretType.DATABASE_CREDENTIAL]),
            ("api-keys", 90, True, [SecretType.API_KEY]),
            ("long-lived", 180, False, [SecretType.SSH_KEY, SecretType.ENCRYPTION_KEY])
        ]
        
        for name, interval, auto, types in policies_data:
            policy = platform.rotation_engine.create_policy(
                name,
                rotation_interval_days=interval,
                auto_rotate=auto,
                secret_types=types
            )
            auto_str = "auto" if auto else "manual"
            print(f"  ✓ {name}: {interval} days, {auto_str}")
            
        # Grant access
        print("\n🔑 Granting Access...")
        
        grants_data = [
            ("db/production/password", "backend-api", "Backend API Service", AccessLevel.READ),
            ("db/production/password", "worker", "Background Worker", AccessLevel.READ),
            ("api/payment-gateway", "checkout-service", "Checkout Service", AccessLevel.READ),
            ("ssh/deploy-key", "ci-pipeline", "CI/CD Pipeline", AccessLevel.ROTATE)
        ]
        
        for secret_name, service_id, service_name, level in grants_data:
            secret = next((s for s in created_secrets if s.name == secret_name), None)
            if secret:
                grant = platform.access_manager.grant(
                    secret.secret_id, service_id, service_name, level
                )
                
                # Log grant
                platform.audit.log(
                    "grant_access", secret.secret_id, secret.name,
                    "admin", "user", success=True,
                    details={"service": service_name, "level": level.value}
                )
                
                print(f"  ✓ {service_name} → {secret_name} ({level.value})")
                
        # Check access
        print("\n🔍 Checking Access...")
        
        checks = [
            ("db/production/password", "backend-api", AccessLevel.READ),
            ("db/production/password", "unknown-service", AccessLevel.READ),
            ("ssh/deploy-key", "ci-pipeline", AccessLevel.ROTATE)
        ]
        
        for secret_name, service_id, level in checks:
            secret = next((s for s in created_secrets if s.name == secret_name), None)
            if secret:
                has_access = platform.access_manager.check_access(
                    secret.secret_id, service_id, level
                )
                status = "✅" if has_access else "❌"
                print(f"  {status} {service_id} → {secret_name} ({level.value})")
                
        # Rotate secrets
        print("\n🔄 Rotating Secrets...")
        
        for secret in created_secrets[:3]:
            result = await platform.rotation_engine.rotate(
                secret.secret_id,
                reason="Scheduled rotation demo"
            )
            
            if result["status"] == "success":
                platform.audit.log(
                    "rotate", secret.secret_id, secret.name,
                    "rotation_engine", "system", success=True
                )
                print(f"  ✓ {secret.name}: new version {result['new_version']}")
            else:
                print(f"  ✗ {secret.name}: {result.get('message', 'Failed')}")
                
        # Emergency rotation
        print("\n🚨 Emergency Rotation...")
        
        emergency_secret = created_secrets[0]
        result = await platform.rotation_engine.rotate(
            emergency_secret.secret_id,
            reason="Emergency: potential exposure"
        )
        
        if result["status"] == "success":
            platform.audit.log(
                "emergency_rotate", emergency_secret.secret_id, emergency_secret.name,
                "security_team", "user", success=True,
                details={"reason": "potential exposure"}
            )
            print(f"  ⚡ {emergency_secret.name}: emergency rotated")
            
        # Show version history
        print("\n📜 Secret Version History:")
        
        for secret in created_secrets[:2]:
            print(f"\n  {secret.name}:")
            for v in secret.versions:
                status = "🟢 active" if v.active else "⚫ inactive"
                print(f"    {v.version_id} - {v.created_at.strftime('%Y-%m-%d %H:%M')} - {status}")
                
        # Audit trail
        print("\n📝 Recent Audit Trail:")
        
        recent = platform.audit.get_recent(hours=24)[:10]
        for entry in recent:
            status = "✓" if entry.success else "✗"
            print(f"  {status} [{entry.timestamp.strftime('%H:%M:%S')}] {entry.action}: {entry.secret_name} by {entry.actor_id}")
            
        # Expiring secrets
        print("\n⏰ Secrets Expiring Soon:")
        
        # Artificially expire one for demo
        created_secrets[1].next_rotation = datetime.now() + timedelta(days=5)
        created_secrets[2].next_rotation = datetime.now() + timedelta(days=3)
        
        expiring = platform.secret_manager.list_expiring(days=7)
        for secret in expiring:
            days_left = (secret.next_rotation - datetime.now()).days if secret.next_rotation else 0
            print(f"  ⚠️ {secret.name}: expires in {days_left} days")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Secrets:")
        print(f"    Total: {stats['total_secrets']}")
        for stype, count in stats['secrets_by_type'].items():
            print(f"    {stype}: {count}")
            
        print(f"\n  Health:")
        print(f"    Expiring Soon: {stats['expiring_soon']}")
        print(f"    Expired: {stats['expired']}")
        
        print(f"\n  Access:")
        print(f"    Active Grants: {stats['active_grants']}")
        print(f"    Policies: {stats['policies']}")
        
        print(f"\n  Audit Entries: {stats['audit_entries']}")
        
        # Dashboard
        print("\n📋 Secrets Rotation Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Secrets Rotation Overview                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Secrets:      {stats['total_secrets']:>10}                        │")
        print(f"  │ Expiring Soon:      {stats['expiring_soon']:>10}                        │")
        print(f"  │ Expired:            {stats['expired']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Active Grants:      {stats['active_grants']:>10}                        │")
        print(f"  │ Rotation Policies:  {stats['policies']:>10}                        │")
        print(f"  │ Audit Entries:      {stats['audit_entries']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Secrets Rotation Platform initialized!")
    print("=" * 60)
