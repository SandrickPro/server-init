#!/usr/bin/env python3
"""
Server Init - Iteration 45: Secret Management & Vault
Управление секретами и Vault

Функционал:
- Secret Vault - хранилище секретов
- Dynamic Secrets - динамические секреты
- Secret Rotation - ротация секретов
- Access Control - контроль доступа
- Audit Logging - аудит логирование
- PKI Management - управление PKI
- Transit Encryption - транзитное шифрование
- Multi-Backend Support - поддержка нескольких бэкендов
"""

import json
import asyncio
import hashlib
import time
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import base64


class SecretType(Enum):
    """Тип секрета"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    ROTATING = "rotating"
    CERTIFICATE = "certificate"
    SSH_KEY = "ssh_key"
    API_KEY = "api_key"


class BackendType(Enum):
    """Тип бэкенда"""
    KV = "kv"
    DATABASE = "database"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    PKI = "pki"
    SSH = "ssh"
    TRANSIT = "transit"


class AccessLevel(Enum):
    """Уровень доступа"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    CREATE = "create"
    UPDATE = "update"
    ROOT = "root"


class AuditAction(Enum):
    """Аудит действие"""
    SECRET_READ = "secret_read"
    SECRET_WRITE = "secret_write"
    SECRET_DELETE = "secret_delete"
    SECRET_ROTATE = "secret_rotate"
    POLICY_CREATE = "policy_create"
    POLICY_UPDATE = "policy_update"
    TOKEN_CREATE = "token_create"
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"


@dataclass
class SecretVersion:
    """Версия секрета"""
    version: int
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    deleted: bool = False
    destroyed: bool = False


@dataclass
class Secret:
    """Секрет"""
    secret_id: str
    path: str
    secret_type: SecretType = SecretType.STATIC
    
    # Версии
    versions: Dict[int, SecretVersion] = field(default_factory=dict)
    current_version: int = 0
    max_versions: int = 10
    
    # Ротация
    rotation_period: Optional[timedelta] = None
    last_rotation: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # TTL
    ttl: Optional[timedelta] = None
    expires_at: Optional[datetime] = None
    
    # Метаданные
    metadata: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DynamicSecretConfig:
    """Конфигурация динамического секрета"""
    config_id: str
    name: str
    backend_type: BackendType
    
    # Настройки
    connection_url: str = ""
    username: str = ""
    password: str = ""
    
    # Создание credentials
    creation_statements: List[str] = field(default_factory=list)
    revocation_statements: List[str] = field(default_factory=list)
    
    # TTL
    default_ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    max_ttl: timedelta = field(default_factory=lambda: timedelta(hours=24))


@dataclass
class DynamicSecret:
    """Динамический секрет"""
    lease_id: str
    config_id: str
    
    # Credentials
    username: str = ""
    password: str = ""
    
    # TTL
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Состояние
    renewable: bool = True
    revoked: bool = False


@dataclass
class Policy:
    """Политика доступа"""
    policy_id: str
    name: str
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Пути
    allowed_paths: List[str] = field(default_factory=list)
    denied_paths: List[str] = field(default_factory=list)
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Token:
    """Токен доступа"""
    token_id: str
    token_hash: str
    
    # Политики
    policies: List[str] = field(default_factory=list)
    
    # TTL
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=24))
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    
    # Метаданные
    display_name: str = ""
    accessor: str = ""
    
    # Состояние
    revoked: bool = False
    renewable: bool = True


@dataclass
class AuditEntry:
    """Запись аудита"""
    entry_id: str
    timestamp: datetime
    action: AuditAction
    
    # Кто
    accessor: str = ""
    token_id: str = ""
    
    # Что
    path: str = ""
    operation: str = ""
    
    # Результат
    success: bool = True
    error: Optional[str] = None
    
    # Детали
    request_data: Dict[str, Any] = field(default_factory=dict)
    response_data: Dict[str, Any] = field(default_factory=dict)
    
    # Источник
    remote_address: str = ""


@dataclass
class Certificate:
    """Сертификат"""
    cert_id: str
    serial_number: str
    
    # Данные
    common_name: str = ""
    organization: str = ""
    
    # Сертификат
    certificate: str = ""
    private_key: str = ""
    ca_chain: List[str] = field(default_factory=list)
    
    # Срок действия
    not_before: datetime = field(default_factory=datetime.now)
    not_after: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Состояние
    revoked: bool = False


class KVBackend:
    """Key-Value бэкенд"""
    
    def __init__(self, mount_path: str = "secret"):
        self.mount_path = mount_path
        self.secrets: Dict[str, Secret] = {}
        
    async def write(self, path: str, data: Dict[str, Any], 
                     cas: Optional[int] = None) -> Dict[str, Any]:
        """Запись секрета"""
        full_path = f"{self.mount_path}/{path}"
        
        if full_path not in self.secrets:
            secret = Secret(
                secret_id=f"secret_{uuid.uuid4().hex[:8]}",
                path=full_path
            )
            self.secrets[full_path] = secret
        else:
            secret = self.secrets[full_path]
            
            # CAS check
            if cas is not None and cas != secret.current_version:
                return {"error": "CAS check failed"}
                
        # Новая версия
        secret.current_version += 1
        version = SecretVersion(
            version=secret.current_version,
            data=data
        )
        
        secret.versions[secret.current_version] = version
        secret.updated_at = datetime.now()
        
        # Cleanup старых версий
        if len(secret.versions) > secret.max_versions:
            oldest = min(secret.versions.keys())
            secret.versions[oldest].destroyed = True
            
        return {
            "path": full_path,
            "version": secret.current_version
        }
        
    async def read(self, path: str, 
                    version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Чтение секрета"""
        full_path = f"{self.mount_path}/{path}"
        
        secret = self.secrets.get(full_path)
        if not secret:
            return None
            
        if version:
            ver = secret.versions.get(version)
        else:
            ver = secret.versions.get(secret.current_version)
            
        if not ver or ver.deleted or ver.destroyed:
            return None
            
        return {
            "data": ver.data,
            "version": ver.version,
            "created_at": ver.created_at.isoformat()
        }
        
    async def delete(self, path: str, versions: Optional[List[int]] = None):
        """Soft delete версий"""
        full_path = f"{self.mount_path}/{path}"
        
        secret = self.secrets.get(full_path)
        if not secret:
            return
            
        if versions:
            for v in versions:
                if v in secret.versions:
                    secret.versions[v].deleted = True
        else:
            # Delete current version
            if secret.current_version in secret.versions:
                secret.versions[secret.current_version].deleted = True
                
    async def undelete(self, path: str, versions: List[int]):
        """Восстановление версий"""
        full_path = f"{self.mount_path}/{path}"
        
        secret = self.secrets.get(full_path)
        if not secret:
            return
            
        for v in versions:
            if v in secret.versions:
                secret.versions[v].deleted = False
                
    async def destroy(self, path: str, versions: List[int]):
        """Полное уничтожение версий"""
        full_path = f"{self.mount_path}/{path}"
        
        secret = self.secrets.get(full_path)
        if not secret:
            return
            
        for v in versions:
            if v in secret.versions:
                secret.versions[v].destroyed = True
                secret.versions[v].data = {}
                
    async def list_secrets(self, path: str = "") -> List[str]:
        """Список секретов"""
        prefix = f"{self.mount_path}/{path}"
        return [
            p.replace(f"{self.mount_path}/", "")
            for p in self.secrets.keys()
            if p.startswith(prefix)
        ]


class DatabaseBackend:
    """Database бэкенд для динамических секретов"""
    
    def __init__(self, mount_path: str = "database"):
        self.mount_path = mount_path
        self.configs: Dict[str, DynamicSecretConfig] = {}
        self.leases: Dict[str, DynamicSecret] = {}
        
    def configure(self, name: str, config: DynamicSecretConfig):
        """Конфигурация connection"""
        self.configs[name] = config
        
    async def generate_credentials(self, role: str) -> Optional[DynamicSecret]:
        """Генерация credentials"""
        config = self.configs.get(role)
        if not config:
            return None
            
        # Генерация username/password
        username = f"v-{role}-{uuid.uuid4().hex[:8]}"
        password = uuid.uuid4().hex
        
        lease = DynamicSecret(
            lease_id=f"lease_{uuid.uuid4().hex[:12]}",
            config_id=config.config_id,
            username=username,
            password=password,
            ttl=config.default_ttl,
            expires_at=datetime.now() + config.default_ttl
        )
        
        self.leases[lease.lease_id] = lease
        
        return lease
        
    async def renew_lease(self, lease_id: str, 
                          increment: Optional[timedelta] = None) -> Optional[DynamicSecret]:
        """Продление lease"""
        lease = self.leases.get(lease_id)
        if not lease or lease.revoked:
            return None
            
        if not lease.renewable:
            return None
            
        config = self.configs.get(lease.config_id)
        if not config:
            return None
            
        # Расчёт нового TTL
        new_ttl = increment or lease.ttl
        
        # Проверка max_ttl
        max_expires = lease.created_at + config.max_ttl
        new_expires = datetime.now() + new_ttl
        
        if new_expires > max_expires:
            new_expires = max_expires
            
        lease.expires_at = new_expires
        lease.ttl = new_expires - datetime.now()
        
        return lease
        
    async def revoke_lease(self, lease_id: str):
        """Отзыв lease"""
        lease = self.leases.get(lease_id)
        if lease:
            lease.revoked = True
            # В реальности тут было бы выполнение revocation_statements
            
    async def list_leases(self, prefix: str = "") -> List[str]:
        """Список leases"""
        return [
            lid for lid, lease in self.leases.items()
            if not lease.revoked
        ]


class PKIBackend:
    """PKI бэкенд"""
    
    def __init__(self, mount_path: str = "pki"):
        self.mount_path = mount_path
        self.ca_certificate: Optional[str] = None
        self.ca_private_key: Optional[str] = None
        self.certificates: Dict[str, Certificate] = {}
        self.serial_counter: int = 1000
        self.crl: List[str] = []
        
    async def generate_root(self, common_name: str) -> Dict[str, Any]:
        """Генерация корневого CA"""
        self.ca_certificate = f"-----BEGIN CERTIFICATE-----\nCA-{common_name}-cert\n-----END CERTIFICATE-----"
        self.ca_private_key = f"-----BEGIN PRIVATE KEY-----\nCA-{common_name}-key\n-----END PRIVATE KEY-----"
        
        return {
            "certificate": self.ca_certificate,
            "issuing_ca": self.ca_certificate
        }
        
    async def issue_certificate(self, common_name: str,
                                 ttl: timedelta = timedelta(days=30),
                                 alt_names: Optional[List[str]] = None) -> Certificate:
        """Выпуск сертификата"""
        self.serial_counter += 1
        
        cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            serial_number=hex(self.serial_counter)[2:],
            common_name=common_name,
            certificate=f"-----BEGIN CERTIFICATE-----\n{common_name}-cert\n-----END CERTIFICATE-----",
            private_key=f"-----BEGIN PRIVATE KEY-----\n{common_name}-key\n-----END PRIVATE KEY-----",
            ca_chain=[self.ca_certificate] if self.ca_certificate else [],
            not_after=datetime.now() + ttl
        )
        
        self.certificates[cert.serial_number] = cert
        
        return cert
        
    async def revoke_certificate(self, serial_number: str):
        """Отзыв сертификата"""
        cert = self.certificates.get(serial_number)
        if cert:
            cert.revoked = True
            self.crl.append(serial_number)
            
    def get_crl(self) -> List[str]:
        """Получение CRL"""
        return self.crl


class TransitBackend:
    """Transit бэкенд для шифрования"""
    
    def __init__(self, mount_path: str = "transit"):
        self.mount_path = mount_path
        self.keys: Dict[str, Dict[str, Any]] = {}
        
    async def create_key(self, name: str, 
                          key_type: str = "aes256-gcm96") -> Dict[str, Any]:
        """Создание ключа шифрования"""
        key = {
            "name": name,
            "type": key_type,
            "key": uuid.uuid4().hex,
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "exportable": False
        }
        
        self.keys[name] = key
        
        return {"name": name, "type": key_type}
        
    async def encrypt(self, key_name: str, plaintext: str) -> str:
        """Шифрование"""
        key = self.keys.get(key_name)
        if not key:
            raise ValueError("Key not found")
            
        # Симуляция шифрования
        encoded = base64.b64encode(plaintext.encode()).decode()
        ciphertext = f"vault:v{key['version']}:{encoded}"
        
        return ciphertext
        
    async def decrypt(self, key_name: str, ciphertext: str) -> str:
        """Расшифровка"""
        key = self.keys.get(key_name)
        if not key:
            raise ValueError("Key not found")
            
        # Парсинг ciphertext
        parts = ciphertext.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid ciphertext format")
            
        encoded = parts[2]
        plaintext = base64.b64decode(encoded).decode()
        
        return plaintext
        
    async def rotate_key(self, key_name: str):
        """Ротация ключа"""
        key = self.keys.get(key_name)
        if key:
            key["version"] += 1
            key["key"] = uuid.uuid4().hex


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        self.backends: List[Dict[str, Any]] = []
        
    def add_backend(self, backend_type: str, config: Dict[str, Any]):
        """Добавление backend для аудита"""
        self.backends.append({
            "type": backend_type,
            "config": config
        })
        
    async def log(self, action: AuditAction, **kwargs) -> str:
        """Логирование действия"""
        entry = AuditEntry(
            entry_id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(),
            action=action,
            **kwargs
        )
        
        self.entries.append(entry)
        
        # Отправка в backends
        for backend in self.backends:
            await self._send_to_backend(backend, entry)
            
        return entry.entry_id
        
    async def _send_to_backend(self, backend: Dict[str, Any], entry: AuditEntry):
        """Отправка в backend"""
        # Симуляция отправки
        pass
        
    def query(self, start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              action: Optional[AuditAction] = None,
              path: Optional[str] = None) -> List[AuditEntry]:
        """Запрос аудит логов"""
        results = self.entries.copy()
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
            
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
            
        if action:
            results = [e for e in results if e.action == action]
            
        if path:
            results = [e for e in results if path in e.path]
            
        return results


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        
    def create_policy(self, name: str, rules: List[Dict[str, Any]]) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            rules=rules
        )
        
        # Парсинг правил
        for rule in rules:
            path = rule.get("path", "")
            if rule.get("capabilities", []):
                policy.allowed_paths.append(path)
                
        self.policies[name] = policy
        
        return policy
        
    def check_access(self, policies: List[str], path: str, 
                      operation: AccessLevel) -> bool:
        """Проверка доступа"""
        for policy_name in policies:
            policy = self.policies.get(policy_name)
            if not policy:
                continue
                
            for rule in policy.rules:
                rule_path = rule.get("path", "")
                
                # Проверка пути
                if self._path_matches(rule_path, path):
                    capabilities = rule.get("capabilities", [])
                    
                    if operation.value in capabilities:
                        return True
                    if "root" in capabilities:
                        return True
                        
        return False
        
    def _path_matches(self, pattern: str, path: str) -> bool:
        """Проверка совпадения пути"""
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return pattern == path


class SecretRotator:
    """Ротатор секретов"""
    
    def __init__(self, kv_backend: KVBackend):
        self.kv_backend = kv_backend
        self.rotation_configs: Dict[str, Dict[str, Any]] = {}
        
    def configure_rotation(self, path: str, 
                            rotation_period: timedelta,
                            generator: Callable[[], str]):
        """Конфигурация ротации"""
        self.rotation_configs[path] = {
            "period": rotation_period,
            "generator": generator,
            "last_rotation": None,
            "next_rotation": datetime.now() + rotation_period
        }
        
    async def rotate(self, path: str) -> Dict[str, Any]:
        """Ротация секрета"""
        config = self.rotation_configs.get(path)
        if not config:
            return {"error": "Rotation not configured for this path"}
            
        # Генерация нового значения
        new_value = config["generator"]()
        
        # Запись
        result = await self.kv_backend.write(path, {"value": new_value})
        
        # Обновление config
        config["last_rotation"] = datetime.now()
        config["next_rotation"] = datetime.now() + config["period"]
        
        return {
            "path": path,
            "rotated_at": config["last_rotation"].isoformat(),
            "next_rotation": config["next_rotation"].isoformat()
        }
        
    async def check_rotations(self) -> List[str]:
        """Проверка необходимости ротации"""
        need_rotation = []
        
        now = datetime.now()
        for path, config in self.rotation_configs.items():
            if config["next_rotation"] <= now:
                need_rotation.append(path)
                
        return need_rotation


class SecretVault:
    """Vault - хранилище секретов"""
    
    def __init__(self):
        # Бэкенды
        self.kv = KVBackend()
        self.database = DatabaseBackend()
        self.pki = PKIBackend()
        self.transit = TransitBackend()
        
        # Сервисы
        self.audit = AuditLogger()
        self.policy_engine = PolicyEngine()
        self.rotator = SecretRotator(self.kv)
        
        # Токены
        self.tokens: Dict[str, Token] = {}
        self.root_token: Optional[str] = None
        
        # Состояние
        self.sealed: bool = True
        self.initialized: bool = False
        
    async def initialize(self, secret_shares: int = 5,
                          secret_threshold: int = 3) -> Dict[str, Any]:
        """Инициализация Vault"""
        if self.initialized:
            return {"error": "Already initialized"}
            
        # Генерация ключей
        keys = [uuid.uuid4().hex for _ in range(secret_shares)]
        self.root_token = uuid.uuid4().hex
        
        self.initialized = True
        
        # Создание root token
        root = Token(
            token_id=self.root_token,
            token_hash=hashlib.sha256(self.root_token.encode()).hexdigest(),
            policies=["root"],
            ttl=timedelta(days=365)
        )
        self.tokens[self.root_token] = root
        
        # Создание root policy
        self.policy_engine.create_policy("root", [
            {"path": "*", "capabilities": ["root"]}
        ])
        
        return {
            "keys": keys,
            "keys_base64": [base64.b64encode(k.encode()).decode() for k in keys],
            "root_token": self.root_token
        }
        
    async def unseal(self, key: str) -> Dict[str, Any]:
        """Разблокировка Vault"""
        # В реальности тут была бы проверка threshold ключей
        self.sealed = False
        
        return {
            "sealed": self.sealed,
            "progress": 3,
            "threshold": 3
        }
        
    async def seal(self):
        """Блокировка Vault"""
        self.sealed = True
        
    def is_sealed(self) -> bool:
        """Проверка статуса"""
        return self.sealed
        
    async def authenticate(self, token: str) -> Optional[Token]:
        """Аутентификация по токену"""
        t = self.tokens.get(token)
        
        if t and not t.revoked and t.expires_at > datetime.now():
            await self.audit.log(
                AuditAction.AUTH_LOGIN,
                token_id=t.token_id,
                success=True
            )
            return t
            
        return None
        
    async def create_token(self, parent_token: str,
                            policies: List[str],
                            ttl: timedelta = timedelta(hours=24)) -> Optional[Token]:
        """Создание токена"""
        parent = await self.authenticate(parent_token)
        if not parent:
            return None
            
        token = Token(
            token_id=uuid.uuid4().hex,
            token_hash=hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest(),
            policies=policies,
            ttl=ttl,
            expires_at=datetime.now() + ttl
        )
        
        self.tokens[token.token_id] = token
        
        await self.audit.log(
            AuditAction.TOKEN_CREATE,
            token_id=parent.token_id,
            success=True
        )
        
        return token
        
    async def read_secret(self, token: str, path: str) -> Optional[Dict[str, Any]]:
        """Чтение секрета"""
        t = await self.authenticate(token)
        if not t:
            return None
            
        # Проверка политик
        if not self.policy_engine.check_access(t.policies, path, AccessLevel.READ):
            await self.audit.log(
                AuditAction.SECRET_READ,
                token_id=t.token_id,
                path=path,
                success=False,
                error="Permission denied"
            )
            return None
            
        # Чтение
        result = await self.kv.read(path)
        
        await self.audit.log(
            AuditAction.SECRET_READ,
            token_id=t.token_id,
            path=path,
            success=True
        )
        
        return result
        
    async def write_secret(self, token: str, path: str, 
                            data: Dict[str, Any]) -> Dict[str, Any]:
        """Запись секрета"""
        t = await self.authenticate(token)
        if not t:
            return {"error": "Unauthorized"}
            
        # Проверка политик
        if not self.policy_engine.check_access(t.policies, path, AccessLevel.WRITE):
            await self.audit.log(
                AuditAction.SECRET_WRITE,
                token_id=t.token_id,
                path=path,
                success=False,
                error="Permission denied"
            )
            return {"error": "Permission denied"}
            
        # Запись
        result = await self.kv.write(path, data)
        
        await self.audit.log(
            AuditAction.SECRET_WRITE,
            token_id=t.token_id,
            path=path,
            success=True
        )
        
        return result
        
    def get_status(self) -> Dict[str, Any]:
        """Статус Vault"""
        return {
            "initialized": self.initialized,
            "sealed": self.sealed,
            "secrets_count": len(self.kv.secrets),
            "tokens_count": len(self.tokens),
            "policies_count": len(self.policy_engine.policies),
            "certificates_count": len(self.pki.certificates),
            "audit_entries": len(self.audit.entries)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 45: Secret Management & Vault")
    print("=" * 60)
    
    async def demo():
        # Создание Vault
        vault = SecretVault()
        print("✓ Secret Vault created")
        
        # Инициализация
        print("\n🔐 Initializing Vault...")
        init_result = await vault.initialize(secret_shares=5, secret_threshold=3)
        
        print(f"  Unseal keys generated: {len(init_result['keys'])}")
        print(f"  Root token: {init_result['root_token'][:16]}...")
        
        root_token = init_result['root_token']
        
        # Unseal
        await vault.unseal("key1")
        print(f"  Vault unsealed: {not vault.is_sealed()}")
        
        # Создание политики
        print("\n📋 Creating policies...")
        
        vault.policy_engine.create_policy("app-secrets", [
            {"path": "secret/data/app/*", "capabilities": ["read", "list"]},
            {"path": "secret/data/db/*", "capabilities": ["read"]}
        ])
        print("  ✓ Created policy: app-secrets")
        
        vault.policy_engine.create_policy("admin", [
            {"path": "secret/*", "capabilities": ["create", "read", "update", "delete", "list"]}
        ])
        print("  ✓ Created policy: admin")
        
        # Создание токена
        print("\n🎟️ Creating tokens...")
        
        app_token = await vault.create_token(
            root_token,
            policies=["app-secrets"],
            ttl=timedelta(hours=1)
        )
        print(f"  ✓ Created app token: {app_token.token_id[:16]}...")
        
        # Запись секретов
        print("\n📝 Writing secrets...")
        
        await vault.write_secret(root_token, "app/database", {
            "username": "dbuser",
            "password": "super-secret-password",
            "host": "db.example.com"
        })
        print("  ✓ Written secret: app/database")
        
        await vault.write_secret(root_token, "app/api", {
            "api_key": "api-key-12345",
            "api_secret": "api-secret-67890"
        })
        print("  ✓ Written secret: app/api")
        
        # Чтение секретов
        print("\n📖 Reading secrets...")
        
        db_secret = await vault.read_secret(root_token, "app/database")
        print(f"  Database username: {db_secret['data']['username']}")
        print(f"  Database password: ***")
        
        # Dynamic secrets (Database)
        print("\n🔄 Dynamic Secrets...")
        
        db_config = DynamicSecretConfig(
            config_id="db_config_1",
            name="postgres",
            backend_type=BackendType.DATABASE,
            connection_url="postgresql://admin:admin@localhost:5432/app",
            creation_statements=["CREATE USER ..."],
            default_ttl=timedelta(hours=1)
        )
        
        vault.database.configure("postgres", db_config)
        print("  ✓ Configured database backend")
        
        creds = await vault.database.generate_credentials("postgres")
        print(f"  Generated credentials:")
        print(f"    Username: {creds.username}")
        print(f"    TTL: {creds.ttl}")
        
        # PKI
        print("\n🔏 PKI Management...")
        
        await vault.pki.generate_root("Example Root CA")
        print("  ✓ Generated Root CA")
        
        cert = await vault.pki.issue_certificate(
            common_name="app.example.com",
            ttl=timedelta(days=30)
        )
        print(f"  ✓ Issued certificate: {cert.common_name}")
        print(f"    Serial: {cert.serial_number}")
        print(f"    Expires: {cert.not_after.date()}")
        
        # Transit encryption
        print("\n🔒 Transit Encryption...")
        
        await vault.transit.create_key("app-key", "aes256-gcm96")
        print("  ✓ Created encryption key: app-key")
        
        plaintext = "Sensitive data to encrypt"
        ciphertext = await vault.transit.encrypt("app-key", plaintext)
        print(f"  Encrypted: {ciphertext[:40]}...")
        
        decrypted = await vault.transit.decrypt("app-key", ciphertext)
        print(f"  Decrypted: {decrypted}")
        
        # Secret rotation
        print("\n🔄 Secret Rotation...")
        
        vault.rotator.configure_rotation(
            "app/api-key",
            rotation_period=timedelta(days=30),
            generator=lambda: uuid.uuid4().hex
        )
        print("  ✓ Configured rotation for app/api-key")
        
        rotation_result = await vault.rotator.rotate("app/api-key")
        print(f"  Rotated at: {rotation_result['rotated_at']}")
        
        # Audit
        print("\n📊 Audit Log...")
        
        recent_audit = vault.audit.query()[-5:]
        print(f"  Recent audit entries: {len(recent_audit)}")
        
        for entry in recent_audit:
            print(f"    {entry.timestamp.strftime('%H:%M:%S')} - {entry.action.value}")
            
        # Status
        status = vault.get_status()
        print(f"\n📈 Vault Status:")
        print(f"  Initialized: {status['initialized']}")
        print(f"  Sealed: {status['sealed']}")
        print(f"  Secrets: {status['secrets_count']}")
        print(f"  Tokens: {status['tokens_count']}")
        print(f"  Certificates: {status['certificates_count']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Secret Management & Vault Platform initialized!")
    print("=" * 60)
