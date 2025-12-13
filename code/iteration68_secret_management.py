#!/usr/bin/env python3
"""
Server Init - Iteration 68: Secret Management Platform
Управление секретами и чувствительными данными

Функционал:
- Secret Storage - хранилище секретов
- Encryption/Decryption - шифрование/дешифрование
- Access Policies - политики доступа
- Secret Rotation - ротация секретов
- Dynamic Secrets - динамические секреты
- Audit Logging - аудит доступа
- Secret Versioning - версионирование
- Lease Management - управление арендой
"""

import json
import asyncio
import hashlib
import base64
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid
import secrets as py_secrets


class SecretType(Enum):
    """Тип секрета"""
    KV = "kv"
    DATABASE = "database"
    AWS = "aws"
    SSH = "ssh"
    PKI = "pki"
    TRANSIT = "transit"
    TOTP = "totp"


class AccessLevel(Enum):
    """Уровень доступа"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class LeaseStatus(Enum):
    """Статус аренды"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class SecretVersion:
    """Версия секрета"""
    version: int
    data: Dict[str, str]  # Зашифрованные данные
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    deleted: bool = False
    deletion_time: Optional[datetime] = None


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    path: str
    
    # Тип
    secret_type: SecretType = SecretType.KV
    
    # Версии
    versions: Dict[int, SecretVersion] = field(default_factory=dict)
    current_version: int = 0
    max_versions: int = 10
    
    # Метаданные
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessPolicy:
    """Политика доступа"""
    policy_id: str
    name: str
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    # {"path": "secret/*", "capabilities": ["read", "list"]}
    
    # Метаданные
    description: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Token:
    """Токен доступа"""
    token_id: str
    accessor: str  # Публичный ID для аудита
    
    # Политики
    policies: List[str] = field(default_factory=list)
    
    # TTL
    ttl_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Ограничения
    num_uses: int = 0  # 0 = unlimited
    uses_remaining: int = 0
    
    # Метаданные
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Статус
    revoked: bool = False


@dataclass
class Lease:
    """Аренда секрета"""
    lease_id: str
    secret_path: str
    
    # TTL
    ttl_seconds: int = 3600
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Статус
    status: LeaseStatus = LeaseStatus.ACTIVE
    
    # Renewable
    renewable: bool = True
    max_ttl_seconds: int = 86400  # 24 часа


@dataclass
class RotationPolicy:
    """Политика ротации"""
    policy_id: str
    secret_path: str
    
    # Расписание
    rotation_period_days: int = 30
    
    # Последняя ротация
    last_rotation: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Статус
    enabled: bool = True
    
    # Уведомления
    notify_before_days: int = 7


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    
    # Операция
    operation: str = ""  # read, write, delete, login, etc.
    path: str = ""
    
    # Идентификация
    token_accessor: str = ""
    client_ip: str = ""
    
    # Результат
    success: bool = True
    error: str = ""
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


class EncryptionEngine:
    """Движок шифрования"""
    
    def __init__(self):
        # В реальности использовался бы HSM или KMS
        self.master_key = py_secrets.token_bytes(32)
        self.key_versions: Dict[int, bytes] = {1: self.master_key}
        self.current_key_version = 1
        
    def encrypt(self, plaintext: str) -> tuple:
        """Шифрование"""
        # Простая симуляция - в реальности AES-256-GCM
        nonce = py_secrets.token_bytes(12)
        
        # XOR шифрование для демо
        key = self.key_versions[self.current_key_version]
        data = plaintext.encode()
        
        encrypted = bytes(d ^ key[i % len(key)] for i, d in enumerate(data))
        
        ciphertext = base64.b64encode(nonce + encrypted).decode()
        
        return ciphertext, self.current_key_version
        
    def decrypt(self, ciphertext: str, key_version: int = None) -> str:
        """Дешифрование"""
        key_ver = key_version or self.current_key_version
        key = self.key_versions.get(key_ver)
        
        if not key:
            raise ValueError("Key version not found")
            
        data = base64.b64decode(ciphertext)
        nonce = data[:12]
        encrypted = data[12:]
        
        decrypted = bytes(d ^ key[i % len(key)] for i, d in enumerate(encrypted))
        
        return decrypted.decode()
        
    def rotate_key(self) -> int:
        """Ротация ключа"""
        self.current_key_version += 1
        self.key_versions[self.current_key_version] = py_secrets.token_bytes(32)
        return self.current_key_version


class SecretStore:
    """Хранилище секретов"""
    
    def __init__(self, encryption: EncryptionEngine):
        self.encryption = encryption
        self.secrets: Dict[str, Secret] = {}
        
    def write(self, path: str, data: Dict[str, str],
               secret_type: SecretType = SecretType.KV,
               metadata: Dict[str, str] = None) -> Secret:
        """Запись секрета"""
        # Шифруем данные
        encrypted_data = {}
        for key, value in data.items():
            ciphertext, _ = self.encryption.encrypt(value)
            encrypted_data[key] = ciphertext
            
        if path not in self.secrets:
            secret = Secret(
                secret_id=f"secret_{uuid.uuid4().hex[:8]}",
                path=path,
                secret_type=secret_type,
                metadata=metadata or {}
            )
            self.secrets[path] = secret
        else:
            secret = self.secrets[path]
            
        # Создаём новую версию
        secret.current_version += 1
        version = SecretVersion(
            version=secret.current_version,
            data=encrypted_data
        )
        
        secret.versions[secret.current_version] = version
        secret.updated_at = datetime.now()
        
        # Удаляем старые версии
        self._cleanup_versions(secret)
        
        return secret
        
    def read(self, path: str, version: int = None) -> Optional[Dict[str, str]]:
        """Чтение секрета"""
        secret = self.secrets.get(path)
        
        if not secret:
            return None
            
        ver = version or secret.current_version
        secret_version = secret.versions.get(ver)
        
        if not secret_version or secret_version.deleted:
            return None
            
        # Дешифруем данные
        decrypted_data = {}
        for key, ciphertext in secret_version.data.items():
            decrypted_data[key] = self.encryption.decrypt(ciphertext)
            
        return decrypted_data
        
    def delete(self, path: str, version: int = None) -> bool:
        """Удаление секрета/версии"""
        secret = self.secrets.get(path)
        
        if not secret:
            return False
            
        if version:
            # Soft delete версии
            if version in secret.versions:
                secret.versions[version].deleted = True
                secret.versions[version].deletion_time = datetime.now()
                return True
        else:
            # Удаление всего секрета
            del self.secrets[path]
            return True
            
        return False
        
    def list_secrets(self, prefix: str = "") -> List[str]:
        """Список секретов"""
        return [path for path in self.secrets.keys() if path.startswith(prefix)]
        
    def _cleanup_versions(self, secret: Secret):
        """Очистка старых версий"""
        if len(secret.versions) > secret.max_versions:
            versions_to_remove = sorted(secret.versions.keys())[:-secret.max_versions]
            for ver in versions_to_remove:
                del secret.versions[ver]


class PolicyManager:
    """Менеджер политик"""
    
    def __init__(self):
        self.policies: Dict[str, AccessPolicy] = {}
        
    def create_policy(self, name: str, rules: List[Dict[str, Any]],
                       **kwargs) -> AccessPolicy:
        """Создание политики"""
        policy = AccessPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            rules=rules,
            **kwargs
        )
        
        self.policies[name] = policy
        return policy
        
    def check_access(self, policy_names: List[str], path: str,
                      operation: str) -> bool:
        """Проверка доступа"""
        for policy_name in policy_names:
            policy = self.policies.get(policy_name)
            
            if not policy:
                continue
                
            for rule in policy.rules:
                if self._path_matches(rule.get("path", ""), path):
                    capabilities = rule.get("capabilities", [])
                    
                    if operation in capabilities or "admin" in capabilities:
                        return True
                        
        return False
        
    def _path_matches(self, pattern: str, path: str) -> bool:
        """Проверка совпадения пути"""
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return pattern == path


class TokenManager:
    """Менеджер токенов"""
    
    def __init__(self):
        self.tokens: Dict[str, Token] = {}
        
    def create_token(self, policies: List[str], ttl_seconds: int = 3600,
                      **kwargs) -> Token:
        """Создание токена"""
        token_value = py_secrets.token_urlsafe(32)
        
        token = Token(
            token_id=hashlib.sha256(token_value.encode()).hexdigest(),
            accessor=f"accessor_{uuid.uuid4().hex[:8]}",
            policies=policies,
            ttl_seconds=ttl_seconds,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
            **kwargs
        )
        
        self.tokens[token.token_id] = token
        
        return token, token_value
        
    def validate_token(self, token_value: str) -> Optional[Token]:
        """Валидация токена"""
        token_id = hashlib.sha256(token_value.encode()).hexdigest()
        token = self.tokens.get(token_id)
        
        if not token:
            return None
            
        if token.revoked:
            return None
            
        if datetime.now() > token.expires_at:
            return None
            
        if token.num_uses > 0:
            if token.uses_remaining <= 0:
                return None
            token.uses_remaining -= 1
            
        return token
        
    def revoke_token(self, token_value: str) -> bool:
        """Отзыв токена"""
        token_id = hashlib.sha256(token_value.encode()).hexdigest()
        token = self.tokens.get(token_id)
        
        if token:
            token.revoked = True
            return True
            
        return False


class LeaseManager:
    """Менеджер аренды"""
    
    def __init__(self):
        self.leases: Dict[str, Lease] = {}
        
    def create_lease(self, secret_path: str, ttl_seconds: int = 3600,
                      **kwargs) -> Lease:
        """Создание аренды"""
        lease = Lease(
            lease_id=f"lease_{uuid.uuid4().hex[:8]}",
            secret_path=secret_path,
            ttl_seconds=ttl_seconds,
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
            **kwargs
        )
        
        self.leases[lease.lease_id] = lease
        return lease
        
    def renew_lease(self, lease_id: str, increment: int = 3600) -> Optional[Lease]:
        """Продление аренды"""
        lease = self.leases.get(lease_id)
        
        if not lease or lease.status != LeaseStatus.ACTIVE:
            return None
            
        if not lease.renewable:
            return None
            
        # Проверяем max_ttl
        new_expires = datetime.now() + timedelta(seconds=increment)
        max_expires = lease.created_at + timedelta(seconds=lease.max_ttl_seconds)
        
        if new_expires > max_expires:
            new_expires = max_expires
            
        lease.expires_at = new_expires
        return lease
        
    def revoke_lease(self, lease_id: str) -> bool:
        """Отзыв аренды"""
        lease = self.leases.get(lease_id)
        
        if lease:
            lease.status = LeaseStatus.REVOKED
            return True
            
        return False
        
    def cleanup_expired(self) -> int:
        """Очистка истёкших аренд"""
        now = datetime.now()
        expired = []
        
        for lease_id, lease in self.leases.items():
            if lease.status == LeaseStatus.ACTIVE and lease.expires_at < now:
                lease.status = LeaseStatus.EXPIRED
                expired.append(lease_id)
                
        return len(expired)


class DynamicSecretEngine:
    """Движок динамических секретов"""
    
    def __init__(self, lease_manager: LeaseManager):
        self.lease_manager = lease_manager
        self.engines: Dict[str, Dict[str, Any]] = {}
        
    def configure_database(self, name: str, connection_url: str,
                            username_template: str = "v_{{name}}_{{random}}",
                            **kwargs):
        """Конфигурация database engine"""
        self.engines[f"database/{name}"] = {
            "type": "database",
            "connection_url": connection_url,
            "username_template": username_template,
            **kwargs
        }
        
    def configure_aws(self, name: str, access_key: str, secret_key: str,
                       region: str = "us-east-1", **kwargs):
        """Конфигурация AWS engine"""
        self.engines[f"aws/{name}"] = {
            "type": "aws",
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region,
            **kwargs
        }
        
    async def generate_credentials(self, engine_path: str,
                                    role: str, ttl: int = 3600) -> Dict[str, Any]:
        """Генерация динамических credentials"""
        engine = self.engines.get(engine_path)
        
        if not engine:
            raise ValueError("Engine not found")
            
        engine_type = engine.get("type")
        
        if engine_type == "database":
            credentials = self._generate_db_credentials(engine, role)
        elif engine_type == "aws":
            credentials = self._generate_aws_credentials(engine, role)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
            
        # Создаём аренду
        lease = self.lease_manager.create_lease(engine_path, ttl)
        
        return {
            "credentials": credentials,
            "lease_id": lease.lease_id,
            "lease_duration": ttl
        }
        
    def _generate_db_credentials(self, engine: Dict[str, Any],
                                  role: str) -> Dict[str, str]:
        """Генерация DB credentials"""
        username = f"v_{role}_{py_secrets.token_hex(4)}"
        password = py_secrets.token_urlsafe(24)
        
        return {
            "username": username,
            "password": password
        }
        
    def _generate_aws_credentials(self, engine: Dict[str, Any],
                                   role: str) -> Dict[str, str]:
        """Генерация AWS credentials"""
        # Симуляция STS assume role
        access_key = f"ASIA{py_secrets.token_hex(8).upper()}"
        secret_key = py_secrets.token_urlsafe(30)
        session_token = py_secrets.token_urlsafe(100)
        
        return {
            "access_key": access_key,
            "secret_key": secret_key,
            "session_token": session_token
        }


class RotationManager:
    """Менеджер ротации секретов"""
    
    def __init__(self, secret_store: SecretStore):
        self.secret_store = secret_store
        self.policies: Dict[str, RotationPolicy] = {}
        
    def create_rotation_policy(self, secret_path: str,
                                rotation_period_days: int = 30,
                                **kwargs) -> RotationPolicy:
        """Создание политики ротации"""
        policy = RotationPolicy(
            policy_id=f"rot_{uuid.uuid4().hex[:8]}",
            secret_path=secret_path,
            rotation_period_days=rotation_period_days,
            next_rotation=datetime.now() + timedelta(days=rotation_period_days),
            **kwargs
        )
        
        self.policies[secret_path] = policy
        return policy
        
    async def rotate_secret(self, secret_path: str,
                             new_value: Dict[str, str] = None) -> bool:
        """Ротация секрета"""
        policy = self.policies.get(secret_path)
        
        if not new_value:
            # Автогенерация
            new_value = {"value": py_secrets.token_urlsafe(32)}
            
        # Записываем новую версию
        self.secret_store.write(secret_path, new_value)
        
        if policy:
            policy.last_rotation = datetime.now()
            policy.next_rotation = datetime.now() + timedelta(days=policy.rotation_period_days)
            
        return True
        
    def get_secrets_needing_rotation(self) -> List[str]:
        """Секреты требующие ротации"""
        now = datetime.now()
        needs_rotation = []
        
        for path, policy in self.policies.items():
            if policy.enabled and policy.next_rotation and policy.next_rotation <= now:
                needs_rotation.append(path)
                
        return needs_rotation


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        
    def log(self, operation: str, path: str, token_accessor: str = "",
             client_ip: str = "", success: bool = True, error: str = "") -> AuditEntry:
        """Запись аудита"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:8]}",
            operation=operation,
            path=path,
            token_accessor=token_accessor,
            client_ip=client_ip,
            success=success,
            error=error
        )
        
        self.entries.append(entry)
        
        # Ограничиваем размер
        if len(self.entries) > 100000:
            self.entries = self.entries[-50000:]
            
        return entry
        
    def query(self, filters: Dict[str, Any] = None,
               limit: int = 100) -> List[AuditEntry]:
        """Запрос записей"""
        result = self.entries
        
        if filters:
            if "operation" in filters:
                result = [e for e in result if e.operation == filters["operation"]]
            if "path_prefix" in filters:
                result = [e for e in result if e.path.startswith(filters["path_prefix"])]
            if "token_accessor" in filters:
                result = [e for e in result if e.token_accessor == filters["token_accessor"]]
            if "success" in filters:
                result = [e for e in result if e.success == filters["success"]]
                
        return result[-limit:]


class SecretManagementPlatform:
    """Платформа управления секретами"""
    
    def __init__(self):
        self.encryption = EncryptionEngine()
        self.secret_store = SecretStore(self.encryption)
        self.policy_manager = PolicyManager()
        self.token_manager = TokenManager()
        self.lease_manager = LeaseManager()
        self.dynamic_secrets = DynamicSecretEngine(self.lease_manager)
        self.rotation_manager = RotationManager(self.secret_store)
        self.audit = AuditLogger()
        
        # Root token
        self._root_token = None
        
    def initialize(self) -> str:
        """Инициализация и получение root token"""
        root_token, root_value = self.token_manager.create_token(
            policies=["root"],
            ttl_seconds=0  # Бессрочный
        )
        root_token.expires_at = datetime.max
        
        # Root policy
        self.policy_manager.create_policy(
            name="root",
            rules=[{"path": "*", "capabilities": ["admin"]}]
        )
        
        self._root_token = root_value
        return root_value
        
    def write_secret(self, token: str, path: str, data: Dict[str, str],
                      client_ip: str = "") -> Dict[str, Any]:
        """Запись секрета"""
        validated_token = self.token_manager.validate_token(token)
        
        if not validated_token:
            self.audit.log("write", path, "", client_ip, False, "Invalid token")
            return {"error": "Invalid token"}
            
        if not self.policy_manager.check_access(validated_token.policies, path, "write"):
            self.audit.log("write", path, validated_token.accessor, client_ip, False, "Access denied")
            return {"error": "Access denied"}
            
        secret = self.secret_store.write(path, data)
        
        self.audit.log("write", path, validated_token.accessor, client_ip, True)
        
        return {
            "path": path,
            "version": secret.current_version,
            "created_at": secret.updated_at.isoformat()
        }
        
    def read_secret(self, token: str, path: str, version: int = None,
                     client_ip: str = "") -> Dict[str, Any]:
        """Чтение секрета"""
        validated_token = self.token_manager.validate_token(token)
        
        if not validated_token:
            self.audit.log("read", path, "", client_ip, False, "Invalid token")
            return {"error": "Invalid token"}
            
        if not self.policy_manager.check_access(validated_token.policies, path, "read"):
            self.audit.log("read", path, validated_token.accessor, client_ip, False, "Access denied")
            return {"error": "Access denied"}
            
        data = self.secret_store.read(path, version)
        
        if data is None:
            self.audit.log("read", path, validated_token.accessor, client_ip, False, "Not found")
            return {"error": "Secret not found"}
            
        self.audit.log("read", path, validated_token.accessor, client_ip, True)
        
        return {"data": data}
        
    def delete_secret(self, token: str, path: str, version: int = None,
                       client_ip: str = "") -> Dict[str, Any]:
        """Удаление секрета"""
        validated_token = self.token_manager.validate_token(token)
        
        if not validated_token:
            return {"error": "Invalid token"}
            
        if not self.policy_manager.check_access(validated_token.policies, path, "delete"):
            return {"error": "Access denied"}
            
        success = self.secret_store.delete(path, version)
        
        self.audit.log("delete", path, validated_token.accessor, client_ip, success)
        
        return {"deleted": success}
        
    def create_token(self, parent_token: str, policies: List[str],
                      ttl_seconds: int = 3600) -> Dict[str, Any]:
        """Создание токена"""
        validated_token = self.token_manager.validate_token(parent_token)
        
        if not validated_token:
            return {"error": "Invalid token"}
            
        token, token_value = self.token_manager.create_token(policies, ttl_seconds)
        
        self.audit.log("token_create", "", validated_token.accessor, "", True)
        
        return {
            "token": token_value,
            "accessor": token.accessor,
            "policies": token.policies,
            "expires_at": token.expires_at.isoformat()
        }
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика платформы"""
        return {
            "secrets": len(self.secret_store.secrets),
            "policies": len(self.policy_manager.policies),
            "tokens": len(self.token_manager.tokens),
            "active_tokens": len([t for t in self.token_manager.tokens.values() 
                                  if not t.revoked and t.expires_at > datetime.now()]),
            "leases": len(self.lease_manager.leases),
            "active_leases": len([l for l in self.lease_manager.leases.values()
                                  if l.status == LeaseStatus.ACTIVE]),
            "rotation_policies": len(self.rotation_manager.policies),
            "audit_entries": len(self.audit.entries),
            "dynamic_engines": len(self.dynamic_secrets.engines)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 68: Secret Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = SecretManagementPlatform()
        print("✓ Secret Management Platform created")
        
        # Инициализация
        print("\n🔐 Initializing vault...")
        root_token = platform.initialize()
        print(f"  ✓ Root token: {root_token[:20]}...")
        
        # Создание политик
        print("\n📜 Creating policies...")
        
        platform.policy_manager.create_policy(
            name="app-secrets",
            rules=[
                {"path": "secret/data/app/*", "capabilities": ["read", "write"]},
                {"path": "secret/metadata/app/*", "capabilities": ["read"]}
            ],
            description="Access to application secrets"
        )
        print("  ✓ Policy: app-secrets")
        
        platform.policy_manager.create_policy(
            name="db-creds",
            rules=[
                {"path": "database/creds/*", "capabilities": ["read"]}
            ],
            description="Access to database credentials"
        )
        print("  ✓ Policy: db-creds")
        
        # Создание токена для приложения
        print("\n🎫 Creating application token...")
        
        token_result = platform.create_token(
            root_token,
            policies=["app-secrets", "db-creds"],
            ttl_seconds=7200
        )
        app_token = token_result["token"]
        print(f"  ✓ Token created: {token_result['accessor']}")
        print(f"  Policies: {token_result['policies']}")
        print(f"  Expires: {token_result['expires_at']}")
        
        # Запись секретов
        print("\n📝 Writing secrets...")
        
        result = platform.write_secret(
            root_token,
            "secret/data/app/config",
            {
                "api_key": "sk-abc123xyz789",
                "api_secret": "super-secret-value",
                "database_url": "postgres://user:pass@localhost/db"
            },
            client_ip="192.168.1.100"
        )
        print(f"  ✓ secret/data/app/config (v{result['version']})")
        
        result = platform.write_secret(
            root_token,
            "secret/data/app/keys",
            {
                "encryption_key": "aes256-key-here",
                "signing_key": "hmac-key-here"
            }
        )
        print(f"  ✓ secret/data/app/keys (v{result['version']})")
        
        # Чтение секретов
        print("\n📖 Reading secrets...")
        
        secret = platform.read_secret(app_token, "secret/data/app/config")
        if "data" in secret:
            print(f"  ✓ Read successful:")
            for key in secret["data"]:
                print(f"    {key}: {secret['data'][key][:20]}...")
                
        # Версионирование
        print("\n📚 Secret versioning...")
        
        # Обновляем секрет
        platform.write_secret(
            root_token,
            "secret/data/app/config",
            {
                "api_key": "sk-new-key-456",
                "api_secret": "new-super-secret",
                "database_url": "postgres://newuser:newpass@localhost/db"
            }
        )
        print("  ✓ Updated to v2")
        
        # Читаем старую версию
        old_secret = platform.secret_store.read("secret/data/app/config", version=1)
        if old_secret:
            print(f"  ✓ v1 still accessible: api_key={old_secret['api_key'][:15]}...")
            
        # Динамические секреты
        print("\n⚡ Dynamic Secrets...")
        
        # Конфигурируем database engine
        platform.dynamic_secrets.configure_database(
            name="postgres",
            connection_url="postgres://admin:admin@localhost:5432/mydb",
            username_template="v_{{name}}_{{random}}"
        )
        print("  ✓ Database engine configured")
        
        # Генерируем credentials
        creds = await platform.dynamic_secrets.generate_credentials(
            "database/postgres",
            role="readonly",
            ttl=3600
        )
        print(f"  ✓ Generated credentials:")
        print(f"    Username: {creds['credentials']['username']}")
        print(f"    Password: {creds['credentials']['password'][:10]}...")
        print(f"    Lease ID: {creds['lease_id']}")
        print(f"    TTL: {creds['lease_duration']}s")
        
        # Конфигурируем AWS engine
        platform.dynamic_secrets.configure_aws(
            name="prod",
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            region="us-east-1"
        )
        print("  ✓ AWS engine configured")
        
        aws_creds = await platform.dynamic_secrets.generate_credentials(
            "aws/prod",
            role="ec2-admin",
            ttl=1800
        )
        print(f"  ✓ AWS credentials generated:")
        print(f"    Access Key: {aws_creds['credentials']['access_key']}")
        
        # Ротация секретов
        print("\n🔄 Secret Rotation...")
        
        rotation_policy = platform.rotation_manager.create_rotation_policy(
            "secret/data/app/keys",
            rotation_period_days=30,
            notify_before_days=7
        )
        print(f"  ✓ Rotation policy: every {rotation_policy.rotation_period_days} days")
        print(f"  Next rotation: {rotation_policy.next_rotation}")
        
        # Выполняем ротацию
        await platform.rotation_manager.rotate_secret(
            "secret/data/app/keys",
            {
                "encryption_key": "new-aes256-key",
                "signing_key": "new-hmac-key"
            }
        )
        print("  ✓ Secret rotated")
        
        # Lease management
        print("\n⏱️ Lease Management...")
        
        # Продление аренды
        lease = platform.lease_manager.leases.get(creds['lease_id'])
        if lease:
            renewed = platform.lease_manager.renew_lease(lease.lease_id, 1800)
            if renewed:
                print(f"  ✓ Lease renewed until {renewed.expires_at}")
                
        # Отзыв аренды
        platform.lease_manager.revoke_lease(creds['lease_id'])
        print("  ✓ Lease revoked")
        
        # Аудит
        print("\n📋 Audit Log:")
        
        recent_audit = platform.audit.query(limit=5)
        for entry in recent_audit:
            status = "✓" if entry.success else "✗"
            print(f"  [{status}] {entry.operation}: {entry.path}")
            
        # Encryption key rotation
        print("\n🔑 Encryption Key Rotation...")
        
        new_version = platform.encryption.rotate_key()
        print(f"  ✓ Rotated to key version {new_version}")
        
        # Статистика
        print("\n📊 Platform Statistics:")
        stats = platform.get_stats()
        print(f"  Secrets: {stats['secrets']}")
        print(f"  Policies: {stats['policies']}")
        print(f"  Active Tokens: {stats['active_tokens']}/{stats['tokens']}")
        print(f"  Active Leases: {stats['active_leases']}/{stats['leases']}")
        print(f"  Rotation Policies: {stats['rotation_policies']}")
        print(f"  Dynamic Engines: {stats['dynamic_engines']}")
        print(f"  Audit Entries: {stats['audit_entries']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Secret Management Platform initialized!")
    print("=" * 60)
