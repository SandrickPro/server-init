#!/usr/bin/env python3
"""
Server Init - Iteration 272: mTLS Manager
Менеджер взаимной TLS аутентификации

Функционал:
- Certificate Authority - центр сертификации
- Certificate Issuance - выдача сертификатов
- Certificate Rotation - ротация сертификатов
- Trust Chain - цепочка доверия
- Revocation - отзыв сертификатов
- Policy Enforcement - применение политик
- SPIFFE/SPIRE Integration - интеграция SPIFFE/SPIRE
- Workload Identity - идентификация рабочих нагрузок
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class CertificateType(Enum):
    """Тип сертификата"""
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    WORKLOAD = "workload"
    CLIENT = "client"
    SERVER = "server"


class CertificateStatus(Enum):
    """Статус сертификата"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class TrustLevel(Enum):
    """Уровень доверия"""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class AuthPolicy(Enum):
    """Политика аутентификации"""
    STRICT = "strict"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"


@dataclass
class KeyPair:
    """Пара ключей"""
    key_id: str
    
    # Algorithm
    algorithm: str = "RSA"
    key_size: int = 2048
    
    # Public key fingerprint
    public_key_fingerprint: str = ""
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Certificate:
    """Сертификат"""
    cert_id: str
    serial_number: str
    
    # Type
    cert_type: CertificateType = CertificateType.WORKLOAD
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    
    # SAN (Subject Alternative Names)
    dns_names: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    uris: List[str] = field(default_factory=list)  # SPIFFE IDs
    
    # Issuer
    issuer_id: str = ""
    
    # Key
    key_pair: Optional[KeyPair] = None
    
    # Validity
    not_before: datetime = field(default_factory=datetime.now)
    not_after: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: CertificateStatus = CertificateStatus.ACTIVE
    
    # Extensions
    is_ca: bool = False
    max_path_length: int = 0
    
    # Fingerprint
    fingerprint_sha256: str = ""


@dataclass
class TrustBundle:
    """Пакет доверия"""
    bundle_id: str
    name: str
    
    # Certificates
    root_certificates: List[Certificate] = field(default_factory=list)
    intermediate_certificates: List[Certificate] = field(default_factory=list)
    
    # Trust domain
    trust_domain: str = ""
    
    # Active
    active: bool = True
    
    # Updated
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkloadIdentity:
    """Идентификация рабочей нагрузки"""
    identity_id: str
    
    # SPIFFE ID
    spiffe_id: str = ""  # spiffe://trust-domain/workload
    
    # Workload info
    workload_name: str = ""
    namespace: str = "default"
    service_account: str = ""
    
    # Certificate
    certificate: Optional[Certificate] = None
    
    # Trust level
    trust_level: TrustLevel = TrustLevel.FULL
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MTLSPolicy:
    """Политика mTLS"""
    policy_id: str
    name: str
    
    # Scope
    namespace: str = "*"
    workload_selector: Dict[str, str] = field(default_factory=dict)
    
    # Mode
    mode: AuthPolicy = AuthPolicy.STRICT
    
    # Authorization
    allowed_identities: List[str] = field(default_factory=list)  # SPIFFE IDs
    
    # Certificate requirements
    min_tls_version: str = "TLSv1.2"
    cipher_suites: List[str] = field(default_factory=list)
    
    # Active
    active: bool = True


@dataclass
class RevocationEntry:
    """Запись об отзыве"""
    entry_id: str
    
    # Certificate
    serial_number: str = ""
    cert_id: str = ""
    
    # Reason
    reason: str = ""
    
    # Revoked at
    revoked_at: datetime = field(default_factory=datetime.now)


@dataclass
class CertificateRequest:
    """Запрос на сертификат"""
    request_id: str
    
    # Subject
    common_name: str = ""
    organization: str = ""
    
    # SAN
    dns_names: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    spiffe_id: str = ""
    
    # Validity
    validity_days: int = 365
    
    # Status
    approved: bool = False
    issued_cert_id: Optional[str] = None
    
    # Timing
    requested_at: datetime = field(default_factory=datetime.now)


class MTLSManager:
    """Менеджер mTLS"""
    
    def __init__(self, trust_domain: str = "cluster.local"):
        self.trust_domain = trust_domain
        self.certificates: Dict[str, Certificate] = {}
        self.trust_bundles: Dict[str, TrustBundle] = {}
        self.workload_identities: Dict[str, WorkloadIdentity] = {}
        self.policies: Dict[str, MTLSPolicy] = {}
        self.revocations: List[RevocationEntry] = []
        self.pending_requests: Dict[str, CertificateRequest] = {}
        self._root_ca: Optional[Certificate] = None
        self._intermediate_ca: Optional[Certificate] = None
        
    def _generate_fingerprint(self, data: str) -> str:
        """Генерация отпечатка"""
        return hashlib.sha256(data.encode()).hexdigest()
        
    def _generate_serial(self) -> str:
        """Генерация серийного номера"""
        return uuid.uuid4().hex[:16].upper()
        
    def initialize_pki(self) -> Certificate:
        """Инициализация PKI"""
        # Create root CA
        key_pair = KeyPair(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            algorithm="RSA",
            key_size=4096,
            public_key_fingerprint=self._generate_fingerprint(f"root-{datetime.now()}")
        )
        
        self._root_ca = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            serial_number=self._generate_serial(),
            cert_type=CertificateType.ROOT_CA,
            common_name=f"{self.trust_domain} Root CA",
            organization="Service Mesh",
            key_pair=key_pair,
            is_ca=True,
            max_path_length=1,
            not_after=datetime.now() + timedelta(days=3650),
            fingerprint_sha256=self._generate_fingerprint(f"root-ca-{datetime.now()}")
        )
        
        self.certificates[self._root_ca.cert_id] = self._root_ca
        
        # Create intermediate CA
        int_key = KeyPair(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            algorithm="RSA",
            key_size=2048,
            public_key_fingerprint=self._generate_fingerprint(f"int-{datetime.now()}")
        )
        
        self._intermediate_ca = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            serial_number=self._generate_serial(),
            cert_type=CertificateType.INTERMEDIATE_CA,
            common_name=f"{self.trust_domain} Intermediate CA",
            organization="Service Mesh",
            issuer_id=self._root_ca.cert_id,
            key_pair=int_key,
            is_ca=True,
            max_path_length=0,
            not_after=datetime.now() + timedelta(days=365),
            fingerprint_sha256=self._generate_fingerprint(f"int-ca-{datetime.now()}")
        )
        
        self.certificates[self._intermediate_ca.cert_id] = self._intermediate_ca
        
        # Create trust bundle
        bundle = TrustBundle(
            bundle_id=f"bundle_{uuid.uuid4().hex[:8]}",
            name="default",
            root_certificates=[self._root_ca],
            intermediate_certificates=[self._intermediate_ca],
            trust_domain=self.trust_domain
        )
        
        self.trust_bundles["default"] = bundle
        
        return self._root_ca
        
    def issue_workload_certificate(self, workload_name: str,
                                   namespace: str,
                                   service_account: str = "default",
                                   dns_names: List[str] = None,
                                   validity_days: int = 30) -> Certificate:
        """Выдача сертификата для рабочей нагрузки"""
        if not self._intermediate_ca:
            self.initialize_pki()
            
        spiffe_id = f"spiffe://{self.trust_domain}/ns/{namespace}/sa/{service_account}"
        
        key_pair = KeyPair(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            algorithm="RSA",
            key_size=2048,
            public_key_fingerprint=self._generate_fingerprint(f"{workload_name}-{datetime.now()}")
        )
        
        cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:8]}",
            serial_number=self._generate_serial(),
            cert_type=CertificateType.WORKLOAD,
            common_name=f"{workload_name}.{namespace}.svc.{self.trust_domain}",
            organization="Service Mesh",
            organizational_unit=namespace,
            dns_names=dns_names or [
                f"{workload_name}",
                f"{workload_name}.{namespace}",
                f"{workload_name}.{namespace}.svc",
                f"{workload_name}.{namespace}.svc.{self.trust_domain}"
            ],
            uris=[spiffe_id],
            issuer_id=self._intermediate_ca.cert_id,
            key_pair=key_pair,
            not_after=datetime.now() + timedelta(days=validity_days),
            fingerprint_sha256=self._generate_fingerprint(f"{workload_name}-cert-{datetime.now()}")
        )
        
        self.certificates[cert.cert_id] = cert
        
        # Create workload identity
        identity = WorkloadIdentity(
            identity_id=f"wid_{uuid.uuid4().hex[:8]}",
            spiffe_id=spiffe_id,
            workload_name=workload_name,
            namespace=namespace,
            service_account=service_account,
            certificate=cert
        )
        
        self.workload_identities[workload_name] = identity
        
        return cert
        
    async def rotate_certificate(self, cert_id: str) -> Optional[Certificate]:
        """Ротация сертификата"""
        old_cert = self.certificates.get(cert_id)
        if not old_cert or old_cert.cert_type in [CertificateType.ROOT_CA, CertificateType.INTERMEDIATE_CA]:
            return None
            
        # Simulate rotation
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        # Find workload
        workload = None
        for wid in self.workload_identities.values():
            if wid.certificate and wid.certificate.cert_id == cert_id:
                workload = wid
                break
                
        if workload:
            new_cert = self.issue_workload_certificate(
                workload.workload_name,
                workload.namespace,
                workload.service_account
            )
            
            # Mark old as expired
            old_cert.status = CertificateStatus.EXPIRED
            
            return new_cert
            
        return None
        
    def revoke_certificate(self, cert_id: str, reason: str = "unspecified"):
        """Отзыв сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return
            
        cert.status = CertificateStatus.REVOKED
        
        entry = RevocationEntry(
            entry_id=f"rev_{uuid.uuid4().hex[:8]}",
            serial_number=cert.serial_number,
            cert_id=cert_id,
            reason=reason
        )
        
        self.revocations.append(entry)
        
    def create_policy(self, name: str,
                     namespace: str = "*",
                     mode: AuthPolicy = AuthPolicy.STRICT) -> MTLSPolicy:
        """Создание политики"""
        policy = MTLSPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            namespace=namespace,
            mode=mode,
            cipher_suites=["TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384"]
        )
        
        self.policies[name] = policy
        return policy
        
    def authorize_identity(self, policy_name: str, spiffe_ids: List[str]):
        """Авторизация идентификации"""
        policy = self.policies.get(policy_name)
        if policy:
            policy.allowed_identities.extend(spiffe_ids)
            
    def verify_certificate(self, cert_id: str) -> Dict[str, Any]:
        """Проверка сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert:
            return {"valid": False, "reason": "certificate not found"}
            
        result = {"valid": True, "cert_id": cert_id}
        
        # Check status
        if cert.status == CertificateStatus.REVOKED:
            return {"valid": False, "reason": "certificate revoked"}
            
        if cert.status == CertificateStatus.EXPIRED:
            return {"valid": False, "reason": "certificate expired"}
            
        # Check validity period
        now = datetime.now()
        if now < cert.not_before:
            return {"valid": False, "reason": "certificate not yet valid"}
            
        if now > cert.not_after:
            cert.status = CertificateStatus.EXPIRED
            return {"valid": False, "reason": "certificate expired"}
            
        # Check chain
        if cert.issuer_id:
            issuer = self.certificates.get(cert.issuer_id)
            if not issuer:
                return {"valid": False, "reason": "issuer not found"}
            if issuer.status != CertificateStatus.ACTIVE:
                return {"valid": False, "reason": "issuer not active"}
                
        result["days_remaining"] = (cert.not_after - now).days
        result["issuer"] = cert.issuer_id
        
        return result
        
    def get_expiring_certificates(self, days: int = 30) -> List[Certificate]:
        """Получение истекающих сертификатов"""
        threshold = datetime.now() + timedelta(days=days)
        
        return [
            cert for cert in self.certificates.values()
            if cert.status == CertificateStatus.ACTIVE
            and cert.not_after <= threshold
            and cert.cert_type == CertificateType.WORKLOAD
        ]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        active = sum(1 for c in self.certificates.values() if c.status == CertificateStatus.ACTIVE)
        expired = sum(1 for c in self.certificates.values() if c.status == CertificateStatus.EXPIRED)
        revoked = sum(1 for c in self.certificates.values() if c.status == CertificateStatus.REVOKED)
        
        return {
            "certificates_total": len(self.certificates),
            "certificates_active": active,
            "certificates_expired": expired,
            "certificates_revoked": revoked,
            "workload_identities": len(self.workload_identities),
            "trust_bundles": len(self.trust_bundles),
            "policies": len(self.policies),
            "revocations": len(self.revocations)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 272: mTLS Manager")
    print("=" * 60)
    
    manager = MTLSManager("production.mesh")
    print("✓ mTLS Manager created")
    
    # Initialize PKI
    print("\n🔐 Initializing PKI...")
    
    root_ca = manager.initialize_pki()
    print(f"  📜 Root CA: {root_ca.common_name}")
    print(f"     Serial: {root_ca.serial_number}")
    print(f"     Valid until: {root_ca.not_after.strftime('%Y-%m-%d')}")
    
    int_ca = manager._intermediate_ca
    print(f"\n  📜 Intermediate CA: {int_ca.common_name}")
    print(f"     Serial: {int_ca.serial_number}")
    print(f"     Valid until: {int_ca.not_after.strftime('%Y-%m-%d')}")
    
    # Issue workload certificates
    print("\n📜 Issuing Workload Certificates...")
    
    workloads = [
        ("api-gateway", "ingress", "api-gateway"),
        ("user-service", "default", "user-sa"),
        ("order-service", "default", "order-sa"),
        ("payment-service", "default", "payment-sa"),
        ("notification-service", "default", "notification-sa"),
    ]
    
    for name, ns, sa in workloads:
        cert = manager.issue_workload_certificate(name, ns, sa, validity_days=30)
        print(f"  📜 {name}: {cert.serial_number}")
        print(f"     SPIFFE: spiffe://{manager.trust_domain}/ns/{ns}/sa/{sa}")
        
    # Create policies
    print("\n📜 Creating mTLS Policies...")
    
    # Strict policy for default namespace
    strict_policy = manager.create_policy("default-strict", "default", AuthPolicy.STRICT)
    manager.authorize_identity("default-strict", [
        f"spiffe://{manager.trust_domain}/ns/ingress/sa/api-gateway",
        f"spiffe://{manager.trust_domain}/ns/default/sa/*"
    ])
    print(f"  📜 default-strict: STRICT mode")
    
    # Permissive for ingress
    perm_policy = manager.create_policy("ingress-permissive", "ingress", AuthPolicy.PERMISSIVE)
    print(f"  📜 ingress-permissive: PERMISSIVE mode")
    
    # Verify certificates
    print("\n✅ Verifying Certificates...")
    
    for cert_id, cert in list(manager.certificates.items())[:4]:
        result = manager.verify_certificate(cert_id)
        if result["valid"]:
            print(f"  ✅ {cert.common_name[:30]}: Valid ({result.get('days_remaining', 'N/A')} days)")
        else:
            print(f"  ❌ {cert.common_name[:30]}: {result['reason']}")
            
    # Rotate a certificate
    print("\n🔄 Rotating Certificate...")
    
    old_cert = list(manager.certificates.values())[-1]
    if old_cert.cert_type == CertificateType.WORKLOAD:
        new_cert = await manager.rotate_certificate(old_cert.cert_id)
        if new_cert:
            print(f"  🔄 Rotated: {old_cert.serial_number} -> {new_cert.serial_number}")
            
    # Revoke a certificate
    print("\n❌ Revoking Certificate...")
    
    cert_to_revoke = list(manager.certificates.values())[3]
    if cert_to_revoke.cert_type == CertificateType.WORKLOAD:
        manager.revoke_certificate(cert_to_revoke.cert_id, "key_compromise")
        print(f"  ❌ Revoked: {cert_to_revoke.serial_number}")
        
    # Display certificates
    print("\n📜 Certificates:")
    
    print("\n  ┌──────────────────────────────────┬─────────────────┬─────────────┬──────────┐")
    print("  │ Common Name                      │ Serial          │ Type        │ Status   │")
    print("  ├──────────────────────────────────┼─────────────────┼─────────────┼──────────┤")
    
    for cert in manager.certificates.values():
        cn = cert.common_name[:32].ljust(32)
        serial = cert.serial_number[:15].ljust(15)
        ctype = cert.cert_type.value[:11].ljust(11)
        status = cert.status.value[:8].ljust(8)
        
        print(f"  │ {cn} │ {serial} │ {ctype} │ {status} │")
        
    print("  └──────────────────────────────────┴─────────────────┴─────────────┴──────────┘")
    
    # Display workload identities
    print("\n🆔 Workload Identities:")
    
    print("\n  ┌─────────────────────┬───────────┬──────────────────────────────────────────────────┐")
    print("  │ Workload            │ Namespace │ SPIFFE ID                                        │")
    print("  ├─────────────────────┼───────────┼──────────────────────────────────────────────────┤")
    
    for identity in manager.workload_identities.values():
        name = identity.workload_name[:19].ljust(19)
        ns = identity.namespace[:9].ljust(9)
        spiffe = identity.spiffe_id[:48].ljust(48)
        
        print(f"  │ {name} │ {ns} │ {spiffe} │")
        
    print("  └─────────────────────┴───────────┴──────────────────────────────────────────────────┘")
    
    # Trust bundle
    print("\n🔒 Trust Bundle:")
    
    bundle = manager.trust_bundles["default"]
    print(f"\n  Name: {bundle.name}")
    print(f"  Trust Domain: {bundle.trust_domain}")
    print(f"  Root CAs: {len(bundle.root_certificates)}")
    print(f"  Intermediate CAs: {len(bundle.intermediate_certificates)}")
    
    # Certificate chain
    print("\n🔗 Certificate Chain:")
    
    workload_cert = list(manager.certificates.values())[-1]
    if workload_cert.cert_type == CertificateType.WORKLOAD:
        print(f"\n  Workload: {workload_cert.common_name}")
        
        if workload_cert.issuer_id:
            issuer = manager.certificates.get(workload_cert.issuer_id)
            if issuer:
                print(f"     └── Issued by: {issuer.common_name}")
                
                if issuer.issuer_id:
                    root = manager.certificates.get(issuer.issuer_id)
                    if root:
                        print(f"            └── Signed by: {root.common_name}")
                        
    # Policies
    print("\n📜 mTLS Policies:")
    
    for policy in manager.policies.values():
        mode_icon = {
            AuthPolicy.STRICT: "🔒",
            AuthPolicy.PERMISSIVE: "🔐",
            AuthPolicy.DISABLED: "🔓"
        }.get(policy.mode, "❓")
        
        print(f"\n  {mode_icon} {policy.name} ({policy.namespace})")
        print(f"     Mode: {policy.mode.value}")
        print(f"     Min TLS: {policy.min_tls_version}")
        if policy.allowed_identities:
            print(f"     Allowed: {len(policy.allowed_identities)} identities")
            
    # Expiring certificates
    print("\n⏰ Certificates Expiring Soon (30 days):")
    
    expiring = manager.get_expiring_certificates(30)
    
    for cert in expiring[:5]:
        days = (cert.not_after - datetime.now()).days
        print(f"  ⏰ {cert.common_name[:30]}: {days} days remaining")
        
    # Revocations
    print("\n❌ Revocation List:")
    
    for rev in manager.revocations:
        print(f"  ❌ Serial: {rev.serial_number}, Reason: {rev.reason}")
        
    # Status distribution
    print("\n📊 Certificate Status Distribution:")
    
    status_counts = {}
    for cert in manager.certificates.values():
        status_counts[cert.status] = status_counts.get(cert.status, 0) + 1
        
    for status, count in status_counts.items():
        icon = {
            CertificateStatus.ACTIVE: "🟢",
            CertificateStatus.EXPIRED: "🟡",
            CertificateStatus.REVOKED: "🔴"
        }.get(status, "⚪")
        bar = "█" * count + "░" * (10 - count)
        print(f"  {icon} {status.value:10s}: [{bar}] {count}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Certificates Total: {stats['certificates_total']}")
    print(f"  Active: {stats['certificates_active']}")
    print(f"  Expired: {stats['certificates_expired']}")
    print(f"  Revoked: {stats['certificates_revoked']}")
    print(f"  Workload Identities: {stats['workload_identities']}")
    print(f"  Policies: {stats['policies']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                         mTLS Dashboard                              │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Certificates:            {stats['certificates_total']:>12}                        │")
    print(f"│ Active:                        {stats['certificates_active']:>12}                        │")
    print(f"│ Workload Identities:           {stats['workload_identities']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Expired:                       {stats['certificates_expired']:>12}                        │")
    print(f"│ Revoked:                       {stats['certificates_revoked']:>12}                        │")
    print(f"│ Policies:                      {stats['policies']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("mTLS Manager initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
