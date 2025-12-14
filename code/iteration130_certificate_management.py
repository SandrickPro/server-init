#!/usr/bin/env python3
"""
Server Init - Iteration 130: Certificate Management Platform
Платформа управления сертификатами

Функционал:
- Certificate Generation - генерация сертификатов
- Certificate Authority - центр сертификации
- Certificate Lifecycle - жизненный цикл сертификатов
- Auto-Renewal - автоматическое обновление
- Certificate Monitoring - мониторинг сертификатов
- Revocation Lists - списки отзыва
- ACME Integration - интеграция с ACME
- Key Management - управление ключами
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random
import hashlib
import base64


class CertificateType(Enum):
    """Тип сертификата"""
    DOMAIN = "domain"
    WILDCARD = "wildcard"
    SAN = "san"  # Subject Alternative Names
    CODE_SIGNING = "code_signing"
    CLIENT = "client"
    INTERMEDIATE = "intermediate"
    ROOT = "root"


class CertificateStatus(Enum):
    """Статус сертификата"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    EXPIRING_SOON = "expiring_soon"


class KeyType(Enum):
    """Тип ключа"""
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    EC_P256 = "ec_p256"
    EC_P384 = "ec_p384"


class ACMEChallenge(Enum):
    """ACME челлендж"""
    HTTP01 = "http01"
    DNS01 = "dns01"
    TLSALPN01 = "tls_alpn01"


@dataclass
class PrivateKey:
    """Приватный ключ"""
    key_id: str
    key_type: KeyType = KeyType.RSA_2048
    
    # Key data (simulated)
    fingerprint: str = ""
    
    # Storage
    stored_in_hsm: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Certificate:
    """Сертификат"""
    cert_id: str
    
    # Type
    cert_type: CertificateType = CertificateType.DOMAIN
    
    # Subject
    common_name: str = ""
    organization: str = ""
    san_names: List[str] = field(default_factory=list)
    
    # Issuer
    issuer_id: str = ""
    issuer_name: str = ""
    
    # Key
    key_id: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: CertificateStatus = CertificateStatus.ACTIVE
    
    # Serial
    serial_number: str = ""
    
    # Fingerprints
    sha256_fingerprint: str = ""
    
    # Renewal
    auto_renew: bool = True
    renewal_days_before: int = 30
    
    # ACME
    acme_order_id: str = ""


@dataclass
class CertificateAuthority:
    """Центр сертификации"""
    ca_id: str
    name: str = ""
    
    # Type
    is_root: bool = False
    
    # Certificate
    cert_id: str = ""
    
    # Subordinates
    subordinate_ids: List[str] = field(default_factory=list)
    
    # CRL
    crl_url: str = ""
    
    # Metrics
    certificates_issued: int = 0


@dataclass
class RevocationEntry:
    """Запись об отзыве"""
    entry_id: str
    cert_id: str = ""
    serial_number: str = ""
    
    # Reason
    reason: str = ""
    
    # Timestamps
    revoked_at: datetime = field(default_factory=datetime.now)


@dataclass
class ACMEOrder:
    """ACME заказ"""
    order_id: str
    domain: str = ""
    
    # Challenge
    challenge_type: ACMEChallenge = ACMEChallenge.HTTP01
    challenge_token: str = ""
    challenge_response: str = ""
    
    # Status
    status: str = "pending"
    
    # Result
    cert_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None


class KeyManager:
    """Менеджер ключей"""
    
    def __init__(self):
        self.keys: Dict[str, PrivateKey] = {}
        
    def generate(self, key_type: KeyType = KeyType.RSA_2048,
                  store_in_hsm: bool = False) -> PrivateKey:
        """Генерация ключа"""
        key = PrivateKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_type=key_type,
            fingerprint=hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32],
            stored_in_hsm=store_in_hsm
        )
        self.keys[key.key_id] = key
        return key
        
    def rotate(self, key_id: str) -> Tuple[PrivateKey, PrivateKey]:
        """Ротация ключа"""
        old_key = self.keys.get(key_id)
        if not old_key:
            return None, None
            
        new_key = self.generate(old_key.key_type, old_key.stored_in_hsm)
        return old_key, new_key


class CertificateManager:
    """Менеджер сертификатов"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.certificates: Dict[str, Certificate] = {}
        
    def create(self, common_name: str, cert_type: CertificateType = CertificateType.DOMAIN,
                san_names: List[str] = None, key_type: KeyType = KeyType.RSA_2048,
                valid_days: int = 365, **kwargs) -> Certificate:
        """Создание сертификата"""
        # Generate key
        key = self.key_manager.generate(key_type)
        
        cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            cert_type=cert_type,
            common_name=common_name,
            san_names=san_names or [],
            key_id=key.key_id,
            valid_until=datetime.now() + timedelta(days=valid_days),
            serial_number=uuid.uuid4().hex[:16].upper(),
            sha256_fingerprint=hashlib.sha256(uuid.uuid4().bytes).hexdigest(),
            **kwargs
        )
        
        self.certificates[cert.cert_id] = cert
        return cert
        
    def renew(self, cert_id: str) -> Certificate:
        """Обновление сертификата"""
        old_cert = self.certificates.get(cert_id)
        if not old_cert:
            return None
            
        # Create new cert with same parameters
        new_cert = self.create(
            old_cert.common_name,
            old_cert.cert_type,
            old_cert.san_names,
            valid_days=365
        )
        new_cert.issuer_id = old_cert.issuer_id
        new_cert.issuer_name = old_cert.issuer_name
        
        # Mark old as expired
        old_cert.status = CertificateStatus.EXPIRED
        
        return new_cert
        
    def check_expiration(self) -> Dict[str, List[Certificate]]:
        """Проверка истечения"""
        now = datetime.now()
        result = {
            "expired": [],
            "expiring_soon": [],
            "valid": []
        }
        
        for cert in self.certificates.values():
            if cert.status == CertificateStatus.REVOKED:
                continue
                
            if cert.valid_until < now:
                cert.status = CertificateStatus.EXPIRED
                result["expired"].append(cert)
            elif cert.valid_until < now + timedelta(days=cert.renewal_days_before):
                cert.status = CertificateStatus.EXPIRING_SOON
                result["expiring_soon"].append(cert)
            else:
                result["valid"].append(cert)
                
        return result


class CAManager:
    """Менеджер центров сертификации"""
    
    def __init__(self, cert_manager: CertificateManager):
        self.cert_manager = cert_manager
        self.cas: Dict[str, CertificateAuthority] = {}
        self.revocations: Dict[str, List[RevocationEntry]] = defaultdict(list)
        
    def create_root_ca(self, name: str, organization: str = "") -> CertificateAuthority:
        """Создание корневого CA"""
        # Create self-signed root cert
        cert = self.cert_manager.create(
            name,
            CertificateType.ROOT,
            valid_days=3650,  # 10 years
            organization=organization
        )
        cert.issuer_name = name
        cert.issuer_id = cert.cert_id
        
        ca = CertificateAuthority(
            ca_id=f"ca_{uuid.uuid4().hex[:8]}",
            name=name,
            is_root=True,
            cert_id=cert.cert_id,
            crl_url=f"http://crl.{name.lower().replace(' ', '-')}.local/crl.pem"
        )
        
        self.cas[ca.ca_id] = ca
        return ca
        
    def create_intermediate_ca(self, name: str, parent_ca_id: str) -> CertificateAuthority:
        """Создание промежуточного CA"""
        parent = self.cas.get(parent_ca_id)
        if not parent:
            return None
            
        # Create intermediate cert signed by parent
        cert = self.cert_manager.create(
            name,
            CertificateType.INTERMEDIATE,
            valid_days=1825  # 5 years
        )
        cert.issuer_id = parent.cert_id
        cert.issuer_name = parent.name
        
        ca = CertificateAuthority(
            ca_id=f"ca_{uuid.uuid4().hex[:8]}",
            name=name,
            is_root=False,
            cert_id=cert.cert_id
        )
        
        parent.subordinate_ids.append(ca.ca_id)
        self.cas[ca.ca_id] = ca
        return ca
        
    def issue_certificate(self, ca_id: str, common_name: str,
                          cert_type: CertificateType = CertificateType.DOMAIN,
                          **kwargs) -> Certificate:
        """Выдача сертификата"""
        ca = self.cas.get(ca_id)
        if not ca:
            return None
            
        cert = self.cert_manager.create(common_name, cert_type, **kwargs)
        cert.issuer_id = ca.cert_id
        cert.issuer_name = ca.name
        
        ca.certificates_issued += 1
        
        return cert
        
    def revoke(self, cert_id: str, reason: str = "unspecified") -> RevocationEntry:
        """Отзыв сертификата"""
        cert = self.cert_manager.certificates.get(cert_id)
        if not cert:
            return None
            
        cert.status = CertificateStatus.REVOKED
        
        entry = RevocationEntry(
            entry_id=f"revoke_{uuid.uuid4().hex[:8]}",
            cert_id=cert_id,
            serial_number=cert.serial_number,
            reason=reason
        )
        
        self.revocations[cert.issuer_id].append(entry)
        return entry


class ACMEClient:
    """ACME клиент"""
    
    def __init__(self, cert_manager: CertificateManager):
        self.cert_manager = cert_manager
        self.orders: Dict[str, ACMEOrder] = {}
        
    async def create_order(self, domain: str,
                            challenge_type: ACMEChallenge = ACMEChallenge.HTTP01) -> ACMEOrder:
        """Создание заказа"""
        order = ACMEOrder(
            order_id=f"order_{uuid.uuid4().hex[:8]}",
            domain=domain,
            challenge_type=challenge_type,
            challenge_token=base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:32],
            challenge_response=base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:64]
        )
        self.orders[order.order_id] = order
        return order
        
    async def validate_challenge(self, order_id: str) -> bool:
        """Валидация челленджа"""
        order = self.orders.get(order_id)
        if not order:
            return False
            
        # Simulate validation
        await asyncio.sleep(0.1)
        
        order.status = "valid"
        order.validated_at = datetime.now()
        return True
        
    async def finalize_order(self, order_id: str) -> Certificate:
        """Завершение заказа"""
        order = self.orders.get(order_id)
        if not order or order.status != "valid":
            return None
            
        # Create certificate
        cert = self.cert_manager.create(
            order.domain,
            CertificateType.DOMAIN,
            valid_days=90,  # Let's Encrypt style
            auto_renew=True
        )
        cert.issuer_name = "ACME CA"
        cert.acme_order_id = order_id
        
        order.cert_id = cert.cert_id
        order.status = "finalized"
        
        return cert


class AutoRenewalService:
    """Сервис автоматического обновления"""
    
    def __init__(self, cert_manager: CertificateManager, acme_client: ACMEClient):
        self.cert_manager = cert_manager
        self.acme_client = acme_client
        self.renewal_history: List[Dict] = []
        
    async def check_and_renew(self) -> List[Certificate]:
        """Проверка и обновление"""
        renewed = []
        
        expiration = self.cert_manager.check_expiration()
        
        for cert in expiration["expiring_soon"]:
            if cert.auto_renew:
                new_cert = await self._renew_certificate(cert)
                if new_cert:
                    renewed.append(new_cert)
                    self.renewal_history.append({
                        "old_cert_id": cert.cert_id,
                        "new_cert_id": new_cert.cert_id,
                        "domain": cert.common_name,
                        "renewed_at": datetime.now()
                    })
                    
        return renewed
        
    async def _renew_certificate(self, cert: Certificate) -> Certificate:
        """Обновление сертификата"""
        if cert.acme_order_id:
            # ACME renewal
            order = await self.acme_client.create_order(cert.common_name)
            await self.acme_client.validate_challenge(order.order_id)
            return await self.acme_client.finalize_order(order.order_id)
        else:
            # Standard renewal
            return self.cert_manager.renew(cert.cert_id)


class CertificateManagementPlatform:
    """Платформа управления сертификатами"""
    
    def __init__(self):
        self.key_manager = KeyManager()
        self.cert_manager = CertificateManager(self.key_manager)
        self.ca_manager = CAManager(self.cert_manager)
        self.acme_client = ACMEClient(self.cert_manager)
        self.auto_renewal = AutoRenewalService(self.cert_manager, self.acme_client)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        certs = list(self.cert_manager.certificates.values())
        
        return {
            "total_certificates": len(certs),
            "active": len([c for c in certs if c.status == CertificateStatus.ACTIVE]),
            "expiring_soon": len([c for c in certs if c.status == CertificateStatus.EXPIRING_SOON]),
            "expired": len([c for c in certs if c.status == CertificateStatus.EXPIRED]),
            "revoked": len([c for c in certs if c.status == CertificateStatus.REVOKED]),
            "total_keys": len(self.key_manager.keys),
            "total_cas": len(self.ca_manager.cas),
            "acme_orders": len(self.acme_client.orders)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 130: Certificate Management Platform")
    print("=" * 60)
    
    async def demo():
        platform = CertificateManagementPlatform()
        print("✓ Certificate Management Platform created")
        
        # Create Root CA
        print("\n🏛️ Creating Certificate Authority Hierarchy...")
        
        root_ca = platform.ca_manager.create_root_ca(
            "Enterprise Root CA",
            organization="Enterprise Corp"
        )
        print(f"  ✓ Root CA: {root_ca.name}")
        
        # Create Intermediate CAs
        issuing_ca = platform.ca_manager.create_intermediate_ca(
            "Enterprise Issuing CA",
            root_ca.ca_id
        )
        print(f"  ✓ Intermediate CA: {issuing_ca.name}")
        
        web_ca = platform.ca_manager.create_intermediate_ca(
            "Web Services CA",
            issuing_ca.ca_id
        )
        print(f"  ✓ Intermediate CA: {web_ca.name}")
        
        # Issue certificates
        print("\n📜 Issuing Certificates...")
        
        domains = [
            ("api.example.com", CertificateType.DOMAIN),
            ("*.example.com", CertificateType.WILDCARD),
            ("app.example.com", CertificateType.SAN)
        ]
        
        issued_certs = []
        for domain, cert_type in domains:
            cert = platform.ca_manager.issue_certificate(
                web_ca.ca_id,
                domain,
                cert_type,
                san_names=["www." + domain.replace("*.", "")] if cert_type == CertificateType.SAN else []
            )
            issued_certs.append(cert)
            print(f"  ✓ {domain} ({cert_type.value})")
            print(f"    Serial: {cert.serial_number}")
            print(f"    Valid until: {cert.valid_until.strftime('%Y-%m-%d')}")
            
        # ACME certificate
        print("\n🔐 Obtaining ACME Certificate (Let's Encrypt style)...")
        
        order = await platform.acme_client.create_order("secure.example.com")
        print(f"  Order created: {order.order_id}")
        print(f"  Challenge type: {order.challenge_type.value}")
        print(f"  Token: {order.challenge_token[:20]}...")
        
        # Validate challenge
        validated = await platform.acme_client.validate_challenge(order.order_id)
        if validated:
            print("  ✓ Challenge validated")
            
        # Finalize order
        acme_cert = await platform.acme_client.finalize_order(order.order_id)
        if acme_cert:
            print(f"  ✓ Certificate issued: {acme_cert.cert_id}")
            print(f"    Valid for: 90 days")
            
        # Generate standalone keys
        print("\n🔑 Managing Keys...")
        
        keys_data = [
            ("RSA 2048", KeyType.RSA_2048, False),
            ("RSA 4096", KeyType.RSA_4096, True),
            ("EC P-256", KeyType.EC_P256, False),
            ("EC P-384", KeyType.EC_P384, True)
        ]
        
        for name, key_type, hsm in keys_data:
            key = platform.key_manager.generate(key_type, store_in_hsm=hsm)
            hsm_status = "HSM" if hsm else "Software"
            print(f"  ✓ {name} ({hsm_status})")
            print(f"    ID: {key.key_id}")
            print(f"    Fingerprint: {key.fingerprint[:16]}...")
            
        # Simulate certificate expiration
        print("\n⏰ Simulating Certificate Expiration...")
        
        # Mark some certs as expiring soon
        for cert in list(platform.cert_manager.certificates.values())[:2]:
            cert.valid_until = datetime.now() + timedelta(days=15)
            
        expiration = platform.cert_manager.check_expiration()
        
        print(f"  Active: {len(expiration['valid'])}")
        print(f"  Expiring Soon: {len(expiration['expiring_soon'])}")
        print(f"  Expired: {len(expiration['expired'])}")
        
        # Auto-renew
        print("\n🔄 Auto-Renewal Process...")
        
        renewed = await platform.auto_renewal.check_and_renew()
        
        print(f"  Renewed {len(renewed)} certificates:")
        for cert in renewed:
            print(f"    ✓ {cert.common_name}")
            
        # Revoke certificate
        print("\n❌ Revoking Certificate...")
        
        if issued_certs:
            revocation = platform.ca_manager.revoke(
                issued_certs[0].cert_id,
                reason="key_compromise"
            )
            print(f"  ✓ Revoked: {issued_certs[0].common_name}")
            print(f"    Reason: {revocation.reason}")
            
        # Certificate inventory
        print("\n📋 Certificate Inventory:")
        
        for cert in platform.cert_manager.certificates.values():
            status_icons = {
                CertificateStatus.ACTIVE: "🟢",
                CertificateStatus.EXPIRING_SOON: "🟡",
                CertificateStatus.EXPIRED: "🔴",
                CertificateStatus.REVOKED: "⛔",
                CertificateStatus.PENDING: "⏳"
            }
            icon = status_icons.get(cert.status, "⚪")
            
            print(f"  {icon} {cert.common_name}")
            print(f"     Type: {cert.cert_type.value}")
            print(f"     Issuer: {cert.issuer_name}")
            print(f"     Valid until: {cert.valid_until.strftime('%Y-%m-%d')}")
            print(f"     Status: {cert.status.value}")
            
        # CA hierarchy
        print("\n🏛️ CA Hierarchy:")
        
        def print_ca(ca_id, indent=0):
            ca = platform.ca_manager.cas.get(ca_id)
            if not ca:
                return
            prefix = "  " * indent
            ca_type = "Root" if ca.is_root else "Intermediate"
            print(f"{prefix}📜 {ca.name} ({ca_type})")
            print(f"{prefix}   Certificates issued: {ca.certificates_issued}")
            for sub_id in ca.subordinate_ids:
                print_ca(sub_id, indent + 1)
                
        for ca in platform.ca_manager.cas.values():
            if ca.is_root:
                print_ca(ca.ca_id)
                
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Certificates: {stats['total_certificates']}")
        print(f"    Active: {stats['active']}")
        print(f"    Expiring Soon: {stats['expiring_soon']}")
        print(f"    Expired: {stats['expired']}")
        print(f"    Revoked: {stats['revoked']}")
        print(f"  Total Keys: {stats['total_keys']}")
        print(f"  Certificate Authorities: {stats['total_cas']}")
        print(f"  ACME Orders: {stats['acme_orders']}")
        
        # Dashboard
        print("\n📋 Certificate Management Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │            Certificate Management Overview                  │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Certificates: {stats['total_certificates']:>10}                        │")
        print(f"  │   Active:           {stats['active']:>10}                        │")
        print(f"  │   Expiring Soon:    {stats['expiring_soon']:>10}                        │")
        print(f"  │   Expired:          {stats['expired']:>10}                        │")
        print(f"  │   Revoked:          {stats['revoked']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Keys:         {stats['total_keys']:>10}                        │")
        print(f"  │ CAs:                {stats['total_cas']:>10}                        │")
        print(f"  │ ACME Orders:        {stats['acme_orders']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Certificate Management Platform initialized!")
    print("=" * 60)
