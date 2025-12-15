#!/usr/bin/env python3
"""
Server Init - Iteration 317: SSL Certificate Manager Platform
Платформа управления SSL сертификатами

Функционал:
- Certificate Management - управление сертификатами
- CSR Generation - генерация запросов на сертификаты
- Certificate Authority - центр сертификации
- Auto-Renewal - автопродление
- ACME Protocol - протокол ACME (Let's Encrypt)
- Certificate Monitoring - мониторинг сертификатов
- Key Management - управление ключами
- Certificate Transparency - прозрачность сертификатов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import hashlib


class CertificateType(Enum):
    """Тип сертификата"""
    DV = "domain_validation"
    OV = "organization_validation"
    EV = "extended_validation"
    SELF_SIGNED = "self_signed"
    INTERNAL = "internal"
    WILDCARD = "wildcard"


class CertificateStatus(Enum):
    """Статус сертификата"""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RENEWING = "renewing"


class KeyAlgorithm(Enum):
    """Алгоритм ключа"""
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA_256 = "ecdsa_256"
    ECDSA_384 = "ecdsa_384"
    ED25519 = "ed25519"


class ACMEChallengeType(Enum):
    """Тип ACME challenge"""
    HTTP_01 = "http-01"
    DNS_01 = "dns-01"
    TLS_ALPN_01 = "tls-alpn-01"


class IssuerType(Enum):
    """Тип издателя"""
    LETS_ENCRYPT = "lets_encrypt"
    DIGICERT = "digicert"
    COMODO = "comodo"
    GLOBALSIGN = "globalsign"
    INTERNAL_CA = "internal_ca"
    SELF = "self"


@dataclass
class PrivateKey:
    """Приватный ключ"""
    key_id: str
    
    # Algorithm
    algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    
    # Key data (simulated)
    key_fingerprint: str = ""
    
    # Security
    is_encrypted: bool = True
    passphrase_protected: bool = True
    
    # Storage
    stored_in_hsm: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CertificateSigningRequest:
    """Запрос на подпись сертификата (CSR)"""
    csr_id: str
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    country: str = ""
    state: str = ""
    locality: str = ""
    email: str = ""
    
    # SANs
    subject_alt_names: List[str] = field(default_factory=list)
    
    # Key
    key_id: str = ""
    
    # CSR data (simulated)
    csr_fingerprint: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Certificate:
    """SSL сертификат"""
    cert_id: str
    name: str
    
    # Domain
    common_name: str = ""
    subject_alt_names: List[str] = field(default_factory=list)
    
    # Type
    cert_type: CertificateType = CertificateType.DV
    
    # Status
    status: CertificateStatus = CertificateStatus.PENDING
    
    # Issuer
    issuer: IssuerType = IssuerType.LETS_ENCRYPT
    issuer_cn: str = ""
    
    # Keys
    key_id: str = ""
    csr_id: str = ""
    
    # Certificate data (simulated)
    serial_number: str = ""
    fingerprint_sha256: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=90))
    
    # Chain
    chain_certificates: List[str] = field(default_factory=list)  # cert_ids
    
    # OCSP
    ocsp_url: str = ""
    
    # Auto-renewal
    auto_renew: bool = True
    renew_days_before: int = 30
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_renewed_at: Optional[datetime] = None
    
    # Usage
    usage_count: int = 0


@dataclass
class ACMEChallenge:
    """ACME Challenge"""
    challenge_id: str
    cert_id: str
    
    # Challenge
    challenge_type: ACMEChallengeType = ACMEChallengeType.HTTP_01
    
    # Domain
    domain: str = ""
    
    # Token
    token: str = ""
    key_authorization: str = ""
    
    # Status
    is_completed: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))


@dataclass
class CertificateAuthority:
    """Центр сертификации"""
    ca_id: str
    name: str
    
    # Type
    is_root: bool = True
    parent_ca_id: str = ""
    
    # Certificate
    cert_id: str = ""
    key_id: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365*10))
    
    # CRL
    crl_url: str = ""
    last_crl_update: Optional[datetime] = None
    
    # Stats
    issued_count: int = 0
    revoked_count: int = 0


@dataclass
class RenewalTask:
    """Задача автопродления"""
    task_id: str
    cert_id: str
    
    # Schedule
    scheduled_at: datetime = field(default_factory=datetime.now)
    
    # Status
    is_completed: bool = False
    is_failed: bool = False
    error_message: str = ""
    
    # Result
    new_cert_id: str = ""


class SSLCertificateManager:
    """Менеджер SSL сертификатов"""
    
    def __init__(self):
        self.private_keys: Dict[str, PrivateKey] = {}
        self.csrs: Dict[str, CertificateSigningRequest] = {}
        self.certificates: Dict[str, Certificate] = {}
        self.challenges: Dict[str, ACMEChallenge] = {}
        self.cas: Dict[str, CertificateAuthority] = {}
        self.renewal_tasks: List[RenewalTask] = []
        
    async def generate_private_key(self, algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048,
                                   encrypt: bool = True) -> PrivateKey:
        """Генерация приватного ключа"""
        key = PrivateKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            algorithm=algorithm,
            key_fingerprint=f"SHA256:{uuid.uuid4().hex}",
            is_encrypted=encrypt
        )
        
        self.private_keys[key.key_id] = key
        return key
        
    async def create_csr(self, key_id: str,
                        common_name: str,
                        organization: str = "",
                        country: str = "",
                        sans: List[str] = None) -> Optional[CertificateSigningRequest]:
        """Создание CSR"""
        key = self.private_keys.get(key_id)
        if not key:
            return None
            
        csr = CertificateSigningRequest(
            csr_id=f"csr_{uuid.uuid4().hex[:8]}",
            common_name=common_name,
            organization=organization,
            country=country,
            subject_alt_names=sans or [common_name],
            key_id=key_id,
            csr_fingerprint=f"SHA256:{uuid.uuid4().hex}"
        )
        
        self.csrs[csr.csr_id] = csr
        return csr
        
    async def request_certificate(self, name: str,
                                  common_name: str,
                                  cert_type: CertificateType = CertificateType.DV,
                                  issuer: IssuerType = IssuerType.LETS_ENCRYPT,
                                  sans: List[str] = None,
                                  key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048,
                                  validity_days: int = 90) -> Certificate:
        """Запрос сертификата"""
        # Generate key
        key = await self.generate_private_key(key_algorithm)
        
        # Generate CSR
        csr = await self.create_csr(key.key_id, common_name, sans=sans)
        
        # Create certificate
        cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            name=name,
            common_name=common_name,
            subject_alt_names=sans or [common_name],
            cert_type=cert_type,
            issuer=issuer,
            key_id=key.key_id,
            csr_id=csr.csr_id if csr else "",
            serial_number=uuid.uuid4().hex.upper(),
            fingerprint_sha256=f"SHA256:{hashlib.sha256(uuid.uuid4().bytes).hexdigest()}",
            valid_to=datetime.now() + timedelta(days=validity_days)
        )
        
        self.certificates[cert.cert_id] = cert
        return cert
        
    async def create_acme_challenge(self, cert_id: str,
                                   domain: str,
                                   challenge_type: ACMEChallengeType = ACMEChallengeType.HTTP_01) -> Optional[ACMEChallenge]:
        """Создание ACME challenge"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return None
            
        token = uuid.uuid4().hex
        key_auth = f"{token}.{uuid.uuid4().hex}"
        
        challenge = ACMEChallenge(
            challenge_id=f"chal_{uuid.uuid4().hex[:8]}",
            cert_id=cert_id,
            challenge_type=challenge_type,
            domain=domain,
            token=token,
            key_authorization=key_auth
        )
        
        self.challenges[challenge.challenge_id] = challenge
        return challenge
        
    async def complete_challenge(self, challenge_id: str) -> bool:
        """Завершение challenge"""
        challenge = self.challenges.get(challenge_id)
        if not challenge:
            return False
            
        # Simulate validation
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        challenge.is_completed = True
        
        # Activate certificate
        cert = self.certificates.get(challenge.cert_id)
        if cert:
            # Check if all challenges completed
            all_completed = all(
                c.is_completed for c in self.challenges.values()
                if c.cert_id == challenge.cert_id
            )
            
            if all_completed:
                cert.status = CertificateStatus.ACTIVE
                
        return True
        
    async def issue_certificate(self, cert_id: str) -> bool:
        """Выпуск сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return False
            
        # Simulate issuance
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        cert.status = CertificateStatus.ACTIVE
        
        # Set issuer CN
        issuer_cns = {
            IssuerType.LETS_ENCRYPT: "Let's Encrypt Authority X3",
            IssuerType.DIGICERT: "DigiCert SHA2 Extended Validation Server CA",
            IssuerType.COMODO: "COMODO RSA Domain Validation Secure Server CA",
            IssuerType.GLOBALSIGN: "GlobalSign GCC R3 DV TLS CA 2020",
            IssuerType.INTERNAL_CA: "Internal CA",
            IssuerType.SELF: cert.common_name
        }
        
        cert.issuer_cn = issuer_cns.get(cert.issuer, "Unknown CA")
        
        return True
        
    async def revoke_certificate(self, cert_id: str, reason: str = "unspecified") -> bool:
        """Отзыв сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return False
            
        cert.status = CertificateStatus.REVOKED
        return True
        
    async def create_internal_ca(self, name: str,
                                is_root: bool = True,
                                parent_ca_id: str = "",
                                validity_years: int = 10) -> CertificateAuthority:
        """Создание внутреннего CA"""
        # Generate key and certificate for CA
        key = await self.generate_private_key(KeyAlgorithm.RSA_4096)
        
        cert = await self.request_certificate(
            name=f"CA: {name}",
            common_name=name,
            cert_type=CertificateType.INTERNAL,
            issuer=IssuerType.INTERNAL_CA,
            validity_days=validity_years * 365
        )
        
        await self.issue_certificate(cert.cert_id)
        
        ca = CertificateAuthority(
            ca_id=f"ca_{uuid.uuid4().hex[:8]}",
            name=name,
            is_root=is_root,
            parent_ca_id=parent_ca_id,
            cert_id=cert.cert_id,
            key_id=key.key_id,
            valid_to=datetime.now() + timedelta(days=validity_years * 365)
        )
        
        self.cas[ca.ca_id] = ca
        return ca
        
    async def issue_from_ca(self, ca_id: str,
                           name: str,
                           common_name: str,
                           sans: List[str] = None,
                           validity_days: int = 365) -> Optional[Certificate]:
        """Выпуск сертификата от внутреннего CA"""
        ca = self.cas.get(ca_id)
        if not ca:
            return None
            
        cert = await self.request_certificate(
            name=name,
            common_name=common_name,
            cert_type=CertificateType.INTERNAL,
            issuer=IssuerType.INTERNAL_CA,
            sans=sans,
            validity_days=validity_days
        )
        
        cert.issuer_cn = ca.name
        cert.chain_certificates.append(ca.cert_id)
        
        await self.issue_certificate(cert.cert_id)
        
        ca.issued_count += 1
        
        return cert
        
    async def schedule_renewal(self, cert_id: str) -> Optional[RenewalTask]:
        """Планирование автопродления"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return None
            
        renewal_date = cert.valid_to - timedelta(days=cert.renew_days_before)
        
        task = RenewalTask(
            task_id=f"renew_{uuid.uuid4().hex[:8]}",
            cert_id=cert_id,
            scheduled_at=renewal_date
        )
        
        self.renewal_tasks.append(task)
        return task
        
    async def process_renewals(self):
        """Обработка задач продления"""
        now = datetime.now()
        
        for task in self.renewal_tasks:
            if task.is_completed or task.is_failed:
                continue
                
            if task.scheduled_at <= now:
                cert = self.certificates.get(task.cert_id)
                if not cert:
                    task.is_failed = True
                    task.error_message = "Certificate not found"
                    continue
                    
                # Simulate renewal
                cert.status = CertificateStatus.RENEWING
                
                try:
                    new_cert = await self.request_certificate(
                        name=f"{cert.name} (renewed)",
                        common_name=cert.common_name,
                        cert_type=cert.cert_type,
                        issuer=cert.issuer,
                        sans=cert.subject_alt_names
                    )
                    
                    await self.issue_certificate(new_cert.cert_id)
                    
                    task.is_completed = True
                    task.new_cert_id = new_cert.cert_id
                    
                    cert.status = CertificateStatus.EXPIRED
                    cert.last_renewed_at = now
                    
                except Exception as e:
                    task.is_failed = True
                    task.error_message = str(e)
                    cert.status = CertificateStatus.ACTIVE
                    
    def get_expiring_certificates(self, days: int = 30) -> List[Certificate]:
        """Получение истекающих сертификатов"""
        cutoff = datetime.now() + timedelta(days=days)
        
        return [
            cert for cert in self.certificates.values()
            if cert.status == CertificateStatus.ACTIVE and cert.valid_to <= cutoff
        ]
        
    def check_certificate_health(self, cert_id: str) -> Dict[str, Any]:
        """Проверка здоровья сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return {"error": "Certificate not found"}
            
        now = datetime.now()
        days_remaining = (cert.valid_to - now).days
        
        issues = []
        warnings = []
        
        # Check expiration
        if days_remaining <= 0:
            issues.append("Certificate has expired")
        elif days_remaining <= 7:
            issues.append(f"Certificate expires in {days_remaining} days")
        elif days_remaining <= 30:
            warnings.append(f"Certificate expires in {days_remaining} days")
            
        # Check status
        if cert.status == CertificateStatus.REVOKED:
            issues.append("Certificate has been revoked")
            
        # Check key strength
        key = self.private_keys.get(cert.key_id)
        if key:
            if key.algorithm in [KeyAlgorithm.RSA_2048]:
                warnings.append("Consider using RSA 4096 or ECDSA for better security")
                
        # Check auto-renewal
        if not cert.auto_renew and days_remaining <= 30:
            warnings.append("Auto-renewal is disabled")
            
        health_score = 100
        health_score -= len(issues) * 30
        health_score -= len(warnings) * 10
        health_score = max(0, health_score)
        
        return {
            "cert_id": cert_id,
            "common_name": cert.common_name,
            "status": cert.status.value,
            "days_remaining": days_remaining,
            "issues": issues,
            "warnings": warnings,
            "health_score": health_score,
            "auto_renew": cert.auto_renew
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_certs = len(self.certificates)
        
        by_status = {}
        for c in self.certificates.values():
            by_status[c.status.value] = by_status.get(c.status.value, 0) + 1
            
        by_type = {}
        for c in self.certificates.values():
            by_type[c.cert_type.value] = by_type.get(c.cert_type.value, 0) + 1
            
        by_issuer = {}
        for c in self.certificates.values():
            by_issuer[c.issuer.value] = by_issuer.get(c.issuer.value, 0) + 1
            
        expiring_30 = len(self.get_expiring_certificates(30))
        expiring_7 = len(self.get_expiring_certificates(7))
        
        active_certs = [c for c in self.certificates.values() 
                       if c.status == CertificateStatus.ACTIVE]
        auto_renew_enabled = sum(1 for c in active_certs if c.auto_renew)
        
        total_keys = len(self.private_keys)
        by_algorithm = {}
        for k in self.private_keys.values():
            by_algorithm[k.algorithm.value] = by_algorithm.get(k.algorithm.value, 0) + 1
            
        pending_renewals = sum(1 for t in self.renewal_tasks 
                              if not t.is_completed and not t.is_failed)
                              
        return {
            "total_certificates": total_certs,
            "by_status": by_status,
            "by_type": by_type,
            "by_issuer": by_issuer,
            "expiring_in_7_days": expiring_7,
            "expiring_in_30_days": expiring_30,
            "auto_renew_enabled": auto_renew_enabled,
            "total_private_keys": total_keys,
            "by_algorithm": by_algorithm,
            "total_csrs": len(self.csrs),
            "total_cas": len(self.cas),
            "pending_renewals": pending_renewals
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 317: SSL Certificate Manager Platform")
    print("=" * 60)
    
    ssl_mgr = SSLCertificateManager()
    print("✓ SSL Certificate Manager created")
    
    # Create internal CA
    print("\n🏛️ Creating Internal Certificate Authority...")
    
    root_ca = await ssl_mgr.create_internal_ca("Root CA", is_root=True, validity_years=20)
    print(f"  🏛️ {root_ca.name} (Root)")
    
    intermediate_ca = await ssl_mgr.create_internal_ca(
        "Intermediate CA", 
        is_root=False, 
        parent_ca_id=root_ca.ca_id,
        validity_years=10
    )
    print(f"  🏛️ {intermediate_ca.name}")
    
    # Request certificates
    print("\n📜 Requesting Certificates...")
    
    cert_requests = [
        ("API Server", "api.example.com", CertificateType.DV, IssuerType.LETS_ENCRYPT, 
         ["api.example.com", "api2.example.com"]),
        ("Web Server", "www.example.com", CertificateType.DV, IssuerType.LETS_ENCRYPT,
         ["www.example.com", "example.com"]),
        ("Mail Server", "mail.example.com", CertificateType.OV, IssuerType.DIGICERT,
         ["mail.example.com", "smtp.example.com", "imap.example.com"]),
        ("Wildcard", "*.example.com", CertificateType.WILDCARD, IssuerType.LETS_ENCRYPT,
         ["*.example.com", "example.com"]),
        ("E-Commerce", "shop.example.com", CertificateType.EV, IssuerType.DIGICERT,
         ["shop.example.com", "checkout.example.com"])
    ]
    
    certs = []
    for name, cn, c_type, issuer, sans in cert_requests:
        cert = await ssl_mgr.request_certificate(name, cn, c_type, issuer, sans)
        certs.append(cert)
        print(f"  📜 {name}: {cn} ({c_type.value})")
        
    # Create ACME challenges
    print("\n🎯 Creating ACME Challenges...")
    
    for cert in certs[:2]:
        for san in cert.subject_alt_names:
            challenge = await ssl_mgr.create_acme_challenge(
                cert.cert_id, san, ACMEChallengeType.HTTP_01
            )
            if challenge:
                print(f"  🎯 {san}: HTTP-01 challenge created")
                
    # Complete challenges and issue certificates
    print("\n✅ Completing Challenges...")
    
    for challenge in ssl_mgr.challenges.values():
        await ssl_mgr.complete_challenge(challenge.challenge_id)
        print(f"  ✅ {challenge.domain} validated")
        
    # Issue remaining certificates
    for cert in certs[2:]:
        await ssl_mgr.issue_certificate(cert.cert_id)
        
    # Issue certificates from internal CA
    print("\n🔏 Issuing Internal Certificates...")
    
    internal_certs_data = [
        ("Database Server", "db.internal.local", ["db.internal.local", "db1.internal.local"]),
        ("Cache Server", "cache.internal.local", ["cache.internal.local"]),
        ("Queue Server", "queue.internal.local", ["queue.internal.local", "rabbitmq.internal.local"])
    ]
    
    internal_certs = []
    for name, cn, sans in internal_certs_data:
        cert = await ssl_mgr.issue_from_ca(intermediate_ca.ca_id, name, cn, sans)
        if cert:
            internal_certs.append(cert)
            print(f"  🔏 {name}: {cn}")
            
    # Schedule renewals
    print("\n📅 Scheduling Renewals...")
    
    for cert in certs:
        task = await ssl_mgr.schedule_renewal(cert.cert_id)
        if task:
            print(f"  📅 {cert.name}: renewal scheduled for {task.scheduled_at.strftime('%Y-%m-%d')}")
            
    # Certificate list
    print("\n📜 Certificates:")
    
    print("\n  ┌─────────────────────────┬──────────────────────────────┬─────────────┬─────────────────────────────────────┐")
    print("  │ Name                    │ Common Name                  │ Type        │ Issuer                              │")
    print("  ├─────────────────────────┼──────────────────────────────┼─────────────┼─────────────────────────────────────┤")
    
    for cert in list(ssl_mgr.certificates.values())[:10]:
        name = cert.name[:23].ljust(23)
        cn = cert.common_name[:28].ljust(28)
        c_type = cert.cert_type.value[:11].ljust(11)
        issuer = cert.issuer_cn[:35].ljust(35)
        
        print(f"  │ {name} │ {cn} │ {c_type} │ {issuer} │")
        
    print("  └─────────────────────────┴──────────────────────────────┴─────────────┴─────────────────────────────────────┘")
    
    # Certificate details
    print("\n📋 Certificate Details:")
    
    for cert in certs[:3]:
        print(f"\n  📜 {cert.name}")
        print(f"     Common Name: {cert.common_name}")
        print(f"     SANs: {', '.join(cert.subject_alt_names)}")
        print(f"     Type: {cert.cert_type.value}")
        print(f"     Status: {cert.status.value}")
        print(f"     Serial: {cert.serial_number[:16]}...")
        print(f"     Fingerprint: {cert.fingerprint_sha256[:32]}...")
        print(f"     Valid: {cert.valid_from.strftime('%Y-%m-%d')} to {cert.valid_to.strftime('%Y-%m-%d')}")
        print(f"     Auto-renew: {'✓' if cert.auto_renew else '✗'}")
        
    # Certificate health
    print("\n💚 Certificate Health:")
    
    print("\n  ┌─────────────────────────┬────────────────┬──────────────────┬────────┬───────────────────────────────────────┐")
    print("  │ Certificate             │ Status         │ Days Remaining   │ Score  │ Issues/Warnings                       │")
    print("  ├─────────────────────────┼────────────────┼──────────────────┼────────┼───────────────────────────────────────┤")
    
    for cert in list(ssl_mgr.certificates.values())[:8]:
        health = ssl_mgr.check_certificate_health(cert.cert_id)
        
        name = cert.name[:23].ljust(23)
        status = health['status'][:14].ljust(14)
        days = str(health['days_remaining']).ljust(16)
        score = f"{health['health_score']}%".ljust(6)
        
        issues_text = ", ".join(health['issues'][:1] + health['warnings'][:1])[:37] if health['issues'] or health['warnings'] else "None"
        issues = issues_text.ljust(37)
        
        print(f"  │ {name} │ {status} │ {days} │ {score} │ {issues} │")
        
    print("  └─────────────────────────┴────────────────┴──────────────────┴────────┴───────────────────────────────────────┘")
    
    # Expiring certificates
    print("\n⚠️ Expiring Certificates (30 days):")
    
    expiring = ssl_mgr.get_expiring_certificates(90)  # Use 90 days for demo
    for cert in expiring[:5]:
        days = (cert.valid_to - datetime.now()).days
        print(f"  ⚠️ {cert.name} ({cert.common_name}) - {days} days remaining")
        
    if not expiring:
        print("  ✓ No certificates expiring soon")
        
    # Private keys
    print("\n🔑 Private Keys:")
    
    print("\n  ┌────────────────────────┬─────────────────────┬───────────────┬─────────────┬────────────┐")
    print("  │ Key ID                 │ Algorithm           │ Encrypted     │ Passphrase  │ HSM        │")
    print("  ├────────────────────────┼─────────────────────┼───────────────┼─────────────┼────────────┤")
    
    for key in list(ssl_mgr.private_keys.values())[:5]:
        key_id = key.key_id[:22].ljust(22)
        algo = key.algorithm.value[:19].ljust(19)
        encrypted = ("✓" if key.is_encrypted else "✗").ljust(13)
        passphrase = ("✓" if key.passphrase_protected else "✗").ljust(11)
        hsm = ("✓" if key.stored_in_hsm else "✗").ljust(10)
        
        print(f"  │ {key_id} │ {algo} │ {encrypted} │ {passphrase} │ {hsm} │")
        
    print("  └────────────────────────┴─────────────────────┴───────────────┴─────────────┴────────────┘")
    
    # Certificate Authorities
    print("\n🏛️ Certificate Authorities:")
    
    for ca in ssl_mgr.cas.values():
        ca_type = "Root" if ca.is_root else "Intermediate"
        days_valid = (ca.valid_to - datetime.now()).days
        
        print(f"\n  🏛️ {ca.name} ({ca_type})")
        print(f"     Valid until: {ca.valid_to.strftime('%Y-%m-%d')} ({days_valid} days)")
        print(f"     Issued: {ca.issued_count} certificates")
        print(f"     Revoked: {ca.revoked_count} certificates")
        
    # Renewal tasks
    print("\n📅 Renewal Tasks:")
    
    pending = [t for t in ssl_mgr.renewal_tasks if not t.is_completed and not t.is_failed]
    print(f"  Pending: {len(pending)}")
    
    for task in pending[:5]:
        cert = ssl_mgr.certificates.get(task.cert_id)
        if cert:
            print(f"  📅 {cert.name} - scheduled {task.scheduled_at.strftime('%Y-%m-%d')}")
            
    # Statistics
    print("\n📊 SSL Certificate Statistics:")
    
    stats = ssl_mgr.get_statistics()
    
    print(f"\n  Total Certificates: {stats['total_certificates']}")
    print("  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  By Type:")
    for c_type, count in stats['by_type'].items():
        print(f"    {c_type}: {count}")
        
    print(f"\n  By Issuer:")
    for issuer, count in stats['by_issuer'].items():
        print(f"    {issuer}: {count}")
        
    print(f"\n  Expiring Certificates:")
    print(f"    Within 7 days: {stats['expiring_in_7_days']}")
    print(f"    Within 30 days: {stats['expiring_in_30_days']}")
    
    print(f"\n  Auto-Renewal Enabled: {stats['auto_renew_enabled']}")
    
    print(f"\n  Private Keys: {stats['total_private_keys']}")
    print("  By Algorithm:")
    for algo, count in stats['by_algorithm'].items():
        print(f"    {algo}: {count}")
        
    print(f"\n  Certificate Authorities: {stats['total_cas']}")
    print(f"  Pending Renewals: {stats['pending_renewals']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                SSL Certificate Manager Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Certificates:          {stats['total_certificates']:>12}                          │")
    print(f"│ Active Certificates:         {stats['by_status'].get('active', 0):>12}                          │")
    print(f"│ Auto-Renewal Enabled:        {stats['auto_renew_enabled']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Expiring (30 days):          {stats['expiring_in_30_days']:>12}                          │")
    print(f"│ Certificate Authorities:     {stats['total_cas']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("SSL Certificate Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
