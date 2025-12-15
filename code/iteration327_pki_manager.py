#!/usr/bin/env python3
"""
Server Init - Iteration 327: PKI Manager Platform
Платформа управления инфраструктурой открытых ключей (PKI)

Функционал:
- Certificate Authority - управление удостоверяющими центрами
- Certificate Management - управление сертификатами
- Key Management - управление ключами
- CSR Processing - обработка запросов на сертификаты
- Certificate Revocation - отзыв сертификатов
- CRL Management - управление списками отзыва
- OCSP Responder - статус сертификатов
- Certificate Templates - шаблоны сертификатов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import hashlib


class CAType(Enum):
    """Тип удостоверяющего центра"""
    ROOT = "root"
    INTERMEDIATE = "intermediate"
    ISSUING = "issuing"
    EXTERNAL = "external"


class CertificateType(Enum):
    """Тип сертификата"""
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    SERVER = "server"
    CLIENT = "client"
    CODE_SIGNING = "code_signing"
    EMAIL = "email"
    WILDCARD = "wildcard"
    SAN = "san"


class CertificateStatus(Enum):
    """Статус сертификата"""
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    SUSPENDED = "suspended"


class KeyAlgorithm(Enum):
    """Алгоритм ключа"""
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"
    ED25519 = "Ed25519"


class RevocationReason(Enum):
    """Причина отзыва"""
    UNSPECIFIED = "unspecified"
    KEY_COMPROMISE = "key_compromise"
    CA_COMPROMISE = "ca_compromise"
    AFFILIATION_CHANGED = "affiliation_changed"
    SUPERSEDED = "superseded"
    CESSATION = "cessation_of_operation"
    HOLD = "certificate_hold"


class CSRStatus(Enum):
    """Статус запроса на сертификат"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ISSUED = "issued"


@dataclass
class KeyPair:
    """Пара ключей"""
    key_id: str
    
    # Algorithm
    algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    key_size: int = 2048
    
    # Keys (simplified)
    public_key_hash: str = ""
    private_key_protected: bool = True
    
    # HSM
    is_hsm_protected: bool = False
    hsm_slot_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class CertificateAuthority:
    """Удостоверяющий центр"""
    ca_id: str
    name: str
    
    # Type
    ca_type: CAType = CAType.INTERMEDIATE
    
    # Hierarchy
    parent_ca_id: Optional[str] = None
    
    # Certificate
    certificate_id: str = ""
    key_pair_id: str = ""
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    country: str = ""
    state: str = ""
    locality: str = ""
    
    # Constraints
    max_path_length: int = 0
    allowed_cert_types: List[CertificateType] = field(default_factory=list)
    
    # Settings
    crl_distribution_points: List[str] = field(default_factory=list)
    ocsp_urls: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Stats
    issued_certificates: int = 0
    revoked_certificates: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    valid_until: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=3650))


@dataclass
class Certificate:
    """Сертификат"""
    certificate_id: str
    
    # Type
    cert_type: CertificateType = CertificateType.SERVER
    
    # Issuer
    issuer_ca_id: str = ""
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    country: str = ""
    
    # SANs
    san_dns: List[str] = field(default_factory=list)
    san_ip: List[str] = field(default_factory=list)
    san_email: List[str] = field(default_factory=list)
    
    # Key
    key_pair_id: str = ""
    algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    
    # Serial
    serial_number: str = ""
    
    # Fingerprints
    sha256_fingerprint: str = ""
    sha1_fingerprint: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))
    
    # Status
    status: CertificateStatus = CertificateStatus.VALID
    
    # Revocation
    revocation_reason: Optional[RevocationReason] = None
    revoked_at: Optional[datetime] = None
    
    # Renewal
    renewal_requested: bool = False
    renewed_cert_id: Optional[str] = None
    
    # Extensions
    key_usage: List[str] = field(default_factory=list)
    extended_key_usage: List[str] = field(default_factory=list)
    is_ca: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CSR:
    """Запрос на подпись сертификата (Certificate Signing Request)"""
    csr_id: str
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    country: str = ""
    
    # SANs
    san_dns: List[str] = field(default_factory=list)
    san_ip: List[str] = field(default_factory=list)
    
    # Key
    algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    public_key_hash: str = ""
    
    # Request
    requestor: str = ""
    requestor_email: str = ""
    
    # Template
    template_id: str = ""
    
    # Status
    status: CSRStatus = CSRStatus.PENDING
    
    # Issued certificate
    certificate_id: str = ""
    
    # Validation
    validation_method: str = "dns"  # dns, http, email, manual
    is_validated: bool = False
    
    # Timestamps
    submitted_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None


@dataclass
class CertificateTemplate:
    """Шаблон сертификата"""
    template_id: str
    name: str
    
    # Type
    cert_type: CertificateType = CertificateType.SERVER
    
    # Validity
    validity_days: int = 365
    
    # Key
    allowed_algorithms: List[KeyAlgorithm] = field(default_factory=list)
    min_key_size: int = 2048
    
    # Extensions
    key_usage: List[str] = field(default_factory=list)
    extended_key_usage: List[str] = field(default_factory=list)
    
    # Policies
    certificate_policies: List[str] = field(default_factory=list)
    
    # Approval
    requires_approval: bool = True
    auto_approve_for: List[str] = field(default_factory=list)  # User/group patterns
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevocationEntry:
    """Запись об отзыве"""
    entry_id: str
    certificate_id: str
    
    # Serial
    serial_number: str = ""
    
    # Reason
    reason: RevocationReason = RevocationReason.UNSPECIFIED
    
    # Revoked by
    revoked_by: str = ""
    
    # Timestamps
    revoked_at: datetime = field(default_factory=datetime.now)
    invalidity_date: Optional[datetime] = None


@dataclass
class CRL:
    """Список отзыва сертификатов"""
    crl_id: str
    ca_id: str
    
    # Number
    crl_number: int = 0
    
    # Entries
    entries: List[str] = field(default_factory=list)  # Entry IDs
    
    # Validity
    this_update: datetime = field(default_factory=datetime.now)
    next_update: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=1))
    
    # Signature
    signature_algorithm: str = "sha256WithRSAEncryption"
    
    # Distribution
    distribution_point: str = ""
    
    # Status
    is_current: bool = True
    
    # Timestamps
    published_at: datetime = field(default_factory=datetime.now)


@dataclass
class OCSPResponse:
    """OCSP ответ"""
    response_id: str
    
    # Certificate
    certificate_serial: str = ""
    
    # Status
    cert_status: CertificateStatus = CertificateStatus.VALID
    
    # Times
    this_update: datetime = field(default_factory=datetime.now)
    next_update: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    
    # Revocation info
    revocation_time: Optional[datetime] = None
    revocation_reason: Optional[RevocationReason] = None
    
    # Nonce
    nonce: str = ""
    
    # Produced
    produced_at: datetime = field(default_factory=datetime.now)


class PKIManager:
    """Менеджер PKI"""
    
    def __init__(self):
        self.certificate_authorities: Dict[str, CertificateAuthority] = {}
        self.certificates: Dict[str, Certificate] = {}
        self.key_pairs: Dict[str, KeyPair] = {}
        self.csrs: Dict[str, CSR] = {}
        self.templates: Dict[str, CertificateTemplate] = {}
        self.revocation_entries: Dict[str, RevocationEntry] = {}
        self.crls: Dict[str, CRL] = {}
        
    async def generate_key_pair(self, algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048,
                                hsm_protected: bool = False,
                                hsm_slot: str = "") -> KeyPair:
        """Генерация пары ключей"""
        key_sizes = {
            KeyAlgorithm.RSA_2048: 2048,
            KeyAlgorithm.RSA_4096: 4096,
            KeyAlgorithm.ECDSA_P256: 256,
            KeyAlgorithm.ECDSA_P384: 384,
            KeyAlgorithm.ED25519: 256
        }
        
        key_pair = KeyPair(
            key_id=f"key_{uuid.uuid4().hex[:12]}",
            algorithm=algorithm,
            key_size=key_sizes.get(algorithm, 2048),
            public_key_hash=hashlib.sha256(uuid.uuid4().bytes).hexdigest(),
            is_hsm_protected=hsm_protected,
            hsm_slot_id=hsm_slot
        )
        
        self.key_pairs[key_pair.key_id] = key_pair
        return key_pair
        
    async def create_ca(self, name: str,
                       ca_type: CAType,
                       common_name: str,
                       organization: str,
                       country: str,
                       parent_ca_id: Optional[str] = None,
                       algorithm: KeyAlgorithm = KeyAlgorithm.RSA_4096,
                       validity_years: int = 10,
                       hsm_protected: bool = False) -> Optional[CertificateAuthority]:
        """Создание удостоверяющего центра"""
        # Validate parent for intermediate/issuing CAs
        if ca_type in [CAType.INTERMEDIATE, CAType.ISSUING] and parent_ca_id:
            parent = self.certificate_authorities.get(parent_ca_id)
            if not parent or not parent.is_active:
                return None
                
        # Generate key pair
        key_pair = await self.generate_key_pair(algorithm, hsm_protected)
        
        ca = CertificateAuthority(
            ca_id=f"ca_{uuid.uuid4().hex[:8]}",
            name=name,
            ca_type=ca_type,
            parent_ca_id=parent_ca_id,
            key_pair_id=key_pair.key_id,
            common_name=common_name,
            organization=organization,
            country=country,
            valid_until=datetime.now() + timedelta(days=validity_years * 365),
            crl_distribution_points=[f"http://crl.{organization.lower().replace(' ', '')}.com/crl/{name.lower()}.crl"],
            ocsp_urls=[f"http://ocsp.{organization.lower().replace(' ', '')}.com"]
        )
        
        # Create CA certificate
        cert = await self._create_ca_certificate(ca, key_pair)
        ca.certificate_id = cert.certificate_id
        
        # Set allowed cert types based on CA type
        if ca_type == CAType.ROOT:
            ca.allowed_cert_types = [CertificateType.INTERMEDIATE_CA]
            ca.max_path_length = 2
        elif ca_type == CAType.INTERMEDIATE:
            ca.allowed_cert_types = [CertificateType.SERVER, CertificateType.CLIENT, CertificateType.CODE_SIGNING]
            ca.max_path_length = 0
        else:
            ca.allowed_cert_types = [CertificateType.SERVER, CertificateType.CLIENT]
            
        self.certificate_authorities[ca.ca_id] = ca
        return ca
        
    async def _create_ca_certificate(self, ca: CertificateAuthority,
                                     key_pair: KeyPair) -> Certificate:
        """Создание сертификата CA"""
        cert_type = CertificateType.ROOT_CA if ca.ca_type == CAType.ROOT else CertificateType.INTERMEDIATE_CA
        
        cert = Certificate(
            certificate_id=f"cert_{uuid.uuid4().hex[:12]}",
            cert_type=cert_type,
            issuer_ca_id=ca.parent_ca_id or ca.ca_id,
            common_name=ca.common_name,
            organization=ca.organization,
            country=ca.country,
            key_pair_id=key_pair.key_id,
            algorithm=key_pair.algorithm,
            serial_number=uuid.uuid4().hex[:16].upper(),
            sha256_fingerprint=hashlib.sha256(uuid.uuid4().bytes).hexdigest().upper(),
            sha1_fingerprint=hashlib.sha1(uuid.uuid4().bytes).hexdigest().upper(),
            valid_until=ca.valid_until,
            is_ca=True,
            key_usage=["keyCertSign", "cRLSign"],
            extended_key_usage=[]
        )
        
        self.certificates[cert.certificate_id] = cert
        return cert
        
    async def create_template(self, name: str,
                             cert_type: CertificateType,
                             validity_days: int = 365,
                             key_usage: List[str] = None,
                             eku: List[str] = None,
                             requires_approval: bool = True) -> CertificateTemplate:
        """Создание шаблона сертификата"""
        template = CertificateTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            cert_type=cert_type,
            validity_days=validity_days,
            allowed_algorithms=[KeyAlgorithm.RSA_2048, KeyAlgorithm.RSA_4096, KeyAlgorithm.ECDSA_P256],
            key_usage=key_usage or ["digitalSignature", "keyEncipherment"],
            extended_key_usage=eku or ["serverAuth", "clientAuth"],
            requires_approval=requires_approval
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def submit_csr(self, common_name: str,
                        organization: str,
                        country: str,
                        san_dns: List[str] = None,
                        san_ip: List[str] = None,
                        algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048,
                        template_id: str = "",
                        requestor: str = "",
                        requestor_email: str = "") -> CSR:
        """Подача запроса на сертификат"""
        csr = CSR(
            csr_id=f"csr_{uuid.uuid4().hex[:12]}",
            common_name=common_name,
            organization=organization,
            country=country,
            san_dns=san_dns or [],
            san_ip=san_ip or [],
            algorithm=algorithm,
            public_key_hash=hashlib.sha256(uuid.uuid4().bytes).hexdigest(),
            template_id=template_id,
            requestor=requestor,
            requestor_email=requestor_email
        )
        
        self.csrs[csr.csr_id] = csr
        return csr
        
    async def approve_csr(self, csr_id: str,
                         approver: str = "") -> bool:
        """Одобрение CSR"""
        csr = self.csrs.get(csr_id)
        if not csr or csr.status != CSRStatus.PENDING:
            return False
            
        csr.status = CSRStatus.APPROVED
        csr.approved_at = datetime.now()
        csr.is_validated = True
        
        return True
        
    async def issue_certificate(self, csr_id: str,
                               ca_id: str,
                               validity_days: int = 365) -> Optional[Certificate]:
        """Выпуск сертификата"""
        csr = self.csrs.get(csr_id)
        if not csr or csr.status != CSRStatus.APPROVED:
            return None
            
        ca = self.certificate_authorities.get(ca_id)
        if not ca or not ca.is_active:
            return None
            
        # Generate key pair
        key_pair = await self.generate_key_pair(csr.algorithm)
        
        # Determine cert type from template or default
        cert_type = CertificateType.SERVER
        key_usage = ["digitalSignature", "keyEncipherment"]
        eku = ["serverAuth", "clientAuth"]
        
        if csr.template_id:
            template = self.templates.get(csr.template_id)
            if template:
                cert_type = template.cert_type
                validity_days = template.validity_days
                key_usage = template.key_usage
                eku = template.extended_key_usage
                
        cert = Certificate(
            certificate_id=f"cert_{uuid.uuid4().hex[:12]}",
            cert_type=cert_type,
            issuer_ca_id=ca_id,
            common_name=csr.common_name,
            organization=csr.organization,
            country=csr.country,
            san_dns=csr.san_dns,
            san_ip=csr.san_ip,
            key_pair_id=key_pair.key_id,
            algorithm=csr.algorithm,
            serial_number=uuid.uuid4().hex[:16].upper(),
            sha256_fingerprint=hashlib.sha256(uuid.uuid4().bytes).hexdigest().upper(),
            sha1_fingerprint=hashlib.sha1(uuid.uuid4().bytes).hexdigest().upper(),
            valid_until=datetime.now() + timedelta(days=validity_days),
            key_usage=key_usage,
            extended_key_usage=eku
        )
        
        self.certificates[cert.certificate_id] = cert
        
        # Update CSR
        csr.status = CSRStatus.ISSUED
        csr.certificate_id = cert.certificate_id
        csr.issued_at = datetime.now()
        
        # Update CA stats
        ca.issued_certificates += 1
        
        return cert
        
    async def revoke_certificate(self, certificate_id: str,
                                reason: RevocationReason = RevocationReason.UNSPECIFIED,
                                revoked_by: str = "") -> bool:
        """Отзыв сертификата"""
        cert = self.certificates.get(certificate_id)
        if not cert or cert.status == CertificateStatus.REVOKED:
            return False
            
        cert.status = CertificateStatus.REVOKED
        cert.revocation_reason = reason
        cert.revoked_at = datetime.now()
        
        # Create revocation entry
        entry = RevocationEntry(
            entry_id=f"rev_{uuid.uuid4().hex[:8]}",
            certificate_id=certificate_id,
            serial_number=cert.serial_number,
            reason=reason,
            revoked_by=revoked_by
        )
        
        self.revocation_entries[entry.entry_id] = entry
        
        # Update CA stats
        ca = self.certificate_authorities.get(cert.issuer_ca_id)
        if ca:
            ca.revoked_certificates += 1
            
        return True
        
    async def renew_certificate(self, certificate_id: str,
                               validity_days: int = 365) -> Optional[Certificate]:
        """Обновление сертификата"""
        old_cert = self.certificates.get(certificate_id)
        if not old_cert or old_cert.status != CertificateStatus.VALID:
            return None
            
        ca = self.certificate_authorities.get(old_cert.issuer_ca_id)
        if not ca or not ca.is_active:
            return None
            
        # Generate new key pair
        key_pair = await self.generate_key_pair(old_cert.algorithm)
        
        new_cert = Certificate(
            certificate_id=f"cert_{uuid.uuid4().hex[:12]}",
            cert_type=old_cert.cert_type,
            issuer_ca_id=old_cert.issuer_ca_id,
            common_name=old_cert.common_name,
            organization=old_cert.organization,
            country=old_cert.country,
            san_dns=old_cert.san_dns,
            san_ip=old_cert.san_ip,
            key_pair_id=key_pair.key_id,
            algorithm=old_cert.algorithm,
            serial_number=uuid.uuid4().hex[:16].upper(),
            sha256_fingerprint=hashlib.sha256(uuid.uuid4().bytes).hexdigest().upper(),
            sha1_fingerprint=hashlib.sha1(uuid.uuid4().bytes).hexdigest().upper(),
            valid_until=datetime.now() + timedelta(days=validity_days),
            key_usage=old_cert.key_usage,
            extended_key_usage=old_cert.extended_key_usage
        )
        
        self.certificates[new_cert.certificate_id] = new_cert
        
        # Update old cert
        old_cert.renewal_requested = True
        old_cert.renewed_cert_id = new_cert.certificate_id
        
        # Update CA stats
        ca.issued_certificates += 1
        
        return new_cert
        
    async def generate_crl(self, ca_id: str) -> Optional[CRL]:
        """Генерация CRL"""
        ca = self.certificate_authorities.get(ca_id)
        if not ca:
            return None
            
        # Find existing CRL
        existing_crl = None
        for crl in self.crls.values():
            if crl.ca_id == ca_id and crl.is_current:
                existing_crl = crl
                existing_crl.is_current = False
                break
                
        # Get revoked certs for this CA
        entry_ids = []
        for entry in self.revocation_entries.values():
            cert = self.certificates.get(entry.certificate_id)
            if cert and cert.issuer_ca_id == ca_id:
                entry_ids.append(entry.entry_id)
                
        crl_number = (existing_crl.crl_number + 1) if existing_crl else 1
        
        crl = CRL(
            crl_id=f"crl_{uuid.uuid4().hex[:8]}",
            ca_id=ca_id,
            crl_number=crl_number,
            entries=entry_ids,
            distribution_point=ca.crl_distribution_points[0] if ca.crl_distribution_points else ""
        )
        
        self.crls[crl.crl_id] = crl
        return crl
        
    async def get_ocsp_response(self, certificate_serial: str) -> OCSPResponse:
        """Получение OCSP ответа"""
        # Find certificate by serial
        cert = None
        for c in self.certificates.values():
            if c.serial_number == certificate_serial:
                cert = c
                break
                
        response = OCSPResponse(
            response_id=f"ocsp_{uuid.uuid4().hex[:8]}",
            certificate_serial=certificate_serial,
            nonce=uuid.uuid4().hex
        )
        
        if cert:
            response.cert_status = cert.status
            if cert.status == CertificateStatus.REVOKED:
                response.revocation_time = cert.revoked_at
                response.revocation_reason = cert.revocation_reason
        else:
            response.cert_status = CertificateStatus.PENDING  # Unknown
            
        return response
        
    def get_expiring_certificates(self, days: int = 30) -> List[Certificate]:
        """Получение сертификатов с истекающим сроком"""
        threshold = datetime.now() + timedelta(days=days)
        expiring = []
        
        for cert in self.certificates.values():
            if cert.status == CertificateStatus.VALID and cert.valid_until <= threshold:
                expiring.append(cert)
                
        return sorted(expiring, key=lambda c: c.valid_until)
        
    def get_certificate_chain(self, certificate_id: str) -> List[Certificate]:
        """Получение цепочки сертификатов"""
        cert = self.certificates.get(certificate_id)
        if not cert:
            return []
            
        chain = [cert]
        current_ca_id = cert.issuer_ca_id
        
        while current_ca_id:
            ca = self.certificate_authorities.get(current_ca_id)
            if not ca or not ca.certificate_id:
                break
                
            ca_cert = self.certificates.get(ca.certificate_id)
            if not ca_cert:
                break
                
            chain.append(ca_cert)
            current_ca_id = ca.parent_ca_id
            
        return chain
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_cas = len(self.certificate_authorities)
        active_cas = sum(1 for ca in self.certificate_authorities.values() if ca.is_active)
        
        total_certs = len(self.certificates)
        valid_certs = sum(1 for c in self.certificates.values() if c.status == CertificateStatus.VALID)
        revoked_certs = sum(1 for c in self.certificates.values() if c.status == CertificateStatus.REVOKED)
        
        by_type = {}
        for cert in self.certificates.values():
            by_type[cert.cert_type.value] = by_type.get(cert.cert_type.value, 0) + 1
            
        by_algorithm = {}
        for cert in self.certificates.values():
            by_algorithm[cert.algorithm.value] = by_algorithm.get(cert.algorithm.value, 0) + 1
            
        pending_csrs = sum(1 for csr in self.csrs.values() if csr.status == CSRStatus.PENDING)
        
        return {
            "total_cas": total_cas,
            "active_cas": active_cas,
            "total_certificates": total_certs,
            "valid_certificates": valid_certs,
            "revoked_certificates": revoked_certs,
            "certificates_by_type": by_type,
            "certificates_by_algorithm": by_algorithm,
            "total_key_pairs": len(self.key_pairs),
            "total_csrs": len(self.csrs),
            "pending_csrs": pending_csrs,
            "total_templates": len(self.templates),
            "total_revocations": len(self.revocation_entries),
            "total_crls": len(self.crls)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 327: PKI Manager Platform")
    print("=" * 60)
    
    pki = PKIManager()
    print("✓ PKI Manager created")
    
    # Create Root CA
    print("\n🏛️ Creating Certificate Authorities...")
    
    root_ca = await pki.create_ca(
        name="Enterprise Root CA",
        ca_type=CAType.ROOT,
        common_name="Enterprise Root CA",
        organization="Enterprise Corp",
        country="US",
        algorithm=KeyAlgorithm.RSA_4096,
        validity_years=20,
        hsm_protected=True
    )
    print(f"  🏛️ Root CA: {root_ca.name}")
    
    # Create Intermediate CA
    intermediate_ca = await pki.create_ca(
        name="Enterprise Intermediate CA",
        ca_type=CAType.INTERMEDIATE,
        common_name="Enterprise Intermediate CA",
        organization="Enterprise Corp",
        country="US",
        parent_ca_id=root_ca.ca_id,
        algorithm=KeyAlgorithm.RSA_4096,
        validity_years=10
    )
    print(f"  🏛️ Intermediate CA: {intermediate_ca.name}")
    
    # Create Issuing CAs
    issuing_cas = []
    issuing_names = [
        ("Web Server CA", "Enterprise Web Server CA"),
        ("Internal CA", "Enterprise Internal CA"),
        ("Code Signing CA", "Enterprise Code Signing CA")
    ]
    
    for name, cn in issuing_names:
        ca = await pki.create_ca(
            name=name,
            ca_type=CAType.ISSUING,
            common_name=cn,
            organization="Enterprise Corp",
            country="US",
            parent_ca_id=intermediate_ca.ca_id,
            algorithm=KeyAlgorithm.RSA_2048,
            validity_years=5
        )
        issuing_cas.append(ca)
        print(f"  🏛️ Issuing CA: {name}")
        
    # Create templates
    print("\n📋 Creating Certificate Templates...")
    
    templates_data = [
        ("Web Server", CertificateType.SERVER, 365, ["digitalSignature", "keyEncipherment"], ["serverAuth"]),
        ("Client Auth", CertificateType.CLIENT, 365, ["digitalSignature"], ["clientAuth"]),
        ("Code Signing", CertificateType.CODE_SIGNING, 365, ["digitalSignature"], ["codeSigning"]),
        ("Wildcard SSL", CertificateType.WILDCARD, 365, ["digitalSignature", "keyEncipherment"], ["serverAuth"]),
        ("Multi-domain", CertificateType.SAN, 365, ["digitalSignature", "keyEncipherment"], ["serverAuth", "clientAuth"])
    ]
    
    templates = []
    for name, cert_type, validity, ku, eku in templates_data:
        tmpl = await pki.create_template(name, cert_type, validity, ku, eku)
        templates.append(tmpl)
        print(f"  📋 {name}")
        
    # Submit CSRs
    print("\n📨 Submitting Certificate Requests...")
    
    csr_data = [
        ("www.enterprise.com", ["www.enterprise.com", "enterprise.com"], []),
        ("api.enterprise.com", ["api.enterprise.com"], ["10.0.1.100"]),
        ("mail.enterprise.com", ["mail.enterprise.com", "smtp.enterprise.com"], []),
        ("*.internal.enterprise.com", ["*.internal.enterprise.com"], []),
        ("jenkins.enterprise.com", ["jenkins.enterprise.com", "ci.enterprise.com"], []),
        ("vault.enterprise.com", ["vault.enterprise.com"], ["10.0.1.50"]),
        ("k8s.enterprise.com", ["k8s.enterprise.com", "kubernetes.enterprise.com"], []),
        ("db.enterprise.com", ["db.enterprise.com"], ["10.0.2.100"])
    ]
    
    csrs = []
    for cn, san_dns, san_ip in csr_data:
        csr = await pki.submit_csr(
            common_name=cn,
            organization="Enterprise Corp",
            country="US",
            san_dns=san_dns,
            san_ip=san_ip,
            template_id=templates[0].template_id,
            requestor="devops@enterprise.com",
            requestor_email="devops@enterprise.com"
        )
        csrs.append(csr)
        print(f"  📨 CSR: {cn}")
        
    # Approve and issue certificates
    print("\n✅ Approving and Issuing Certificates...")
    
    certificates = []
    for csr in csrs:
        await pki.approve_csr(csr.csr_id, "ca-admin@enterprise.com")
        cert = await pki.issue_certificate(csr.csr_id, issuing_cas[0].ca_id)
        if cert:
            certificates.append(cert)
            
    print(f"  ✓ Issued {len(certificates)} certificates")
    
    # Revoke some certificates
    print("\n🚫 Revoking Certificates...")
    
    revoke_reasons = [
        (RevocationReason.SUPERSEDED, "Replaced with new certificate"),
        (RevocationReason.KEY_COMPROMISE, "Private key leaked")
    ]
    
    for i, (reason, desc) in enumerate(revoke_reasons):
        if i < len(certificates):
            await pki.revoke_certificate(
                certificates[i].certificate_id,
                reason,
                "ca-admin@enterprise.com"
            )
            print(f"  🚫 Revoked: {certificates[i].common_name} ({reason.value})")
            
    # Renew certificates
    print("\n🔄 Renewing Certificates...")
    
    for cert in certificates[2:4]:
        renewed = await pki.renew_certificate(cert.certificate_id)
        if renewed:
            print(f"  🔄 Renewed: {cert.common_name}")
            
    # Generate CRL
    print("\n📜 Generating CRLs...")
    
    for ca in [root_ca, intermediate_ca] + issuing_cas:
        crl = await pki.generate_crl(ca.ca_id)
        if crl:
            print(f"  📜 CRL #{crl.crl_number} for {ca.name}")
            
    # Check OCSP
    print("\n🔍 Checking OCSP Status...")
    
    for cert in certificates[:4]:
        response = await pki.get_ocsp_response(cert.serial_number)
        status_icon = "✓" if response.cert_status == CertificateStatus.VALID else "✗"
        print(f"  {status_icon} {cert.common_name}: {response.cert_status.value}")
        
    # Get expiring certificates
    print("\n⏰ Expiring Certificates (next 400 days):")
    
    expiring = pki.get_expiring_certificates(400)
    for cert in expiring[:5]:
        days_left = (cert.valid_until - datetime.now()).days
        print(f"  ⏰ {cert.common_name}: {days_left} days left")
        
    # Certificate chain
    print("\n🔗 Certificate Chain:")
    
    if certificates:
        chain = pki.get_certificate_chain(certificates[3].certificate_id)
        for i, cert in enumerate(chain):
            indent = "  " * (i + 1)
            print(f"{indent}↳ {cert.common_name}")
            
    # CA hierarchy
    print("\n🏛️ CA Hierarchy:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Certificate Authority                      │ Type         │ Issued │ Revoked │ Valid │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────┤")
    
    all_cas = [root_ca, intermediate_ca] + issuing_cas
    for ca in all_cas:
        prefix = ""
        if ca.ca_type == CAType.INTERMEDIATE:
            prefix = "  └─"
        elif ca.ca_type == CAType.ISSUING:
            prefix = "    └─"
            
        name = f"{prefix}{ca.name}"[:40].ljust(40)
        ca_type = ca.ca_type.value[:12].ljust(12)
        issued = str(ca.issued_certificates).rjust(6)
        revoked = str(ca.revoked_certificates).rjust(7)
        valid = "✓ Yes" if ca.is_active else "✗ No"
        valid = valid[:5].ljust(5)
        
        print(f"  │ {name} │ {ca_type} │ {issued} │ {revoked} │ {valid} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Templates
    print("\n📋 Certificate Templates:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Template         │ Type           │ Validity │ Key Usage                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────┤")
    
    for tmpl in templates:
        name = tmpl.name[:16].ljust(16)
        cert_type = tmpl.cert_type.value[:14].ljust(14)
        validity = f"{tmpl.validity_days}d".ljust(8)
        ku = ", ".join(tmpl.key_usage)[:31].ljust(31)
        
        print(f"  │ {name} │ {cert_type} │ {validity} │ {ku} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────┘")
    
    # Certificates
    print("\n📜 Issued Certificates:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Common Name                    │ Type     │ Algorithm │ Status   │ Valid Until          │ Fingerprint│")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cert in list(pki.certificates.values())[-10:]:
        if not cert.is_ca:
            cn = cert.common_name[:30].ljust(30)
            cert_type = cert.cert_type.value[:8].ljust(8)
            algo = cert.algorithm.value[:9].ljust(9)
            
            status_icon = {
                "valid": "✓",
                "revoked": "✗",
                "expired": "⚠",
                "pending": "○"
            }.get(cert.status.value, "?")
            status = f"{status_icon} {cert.status.value}"[:8].ljust(8)
            
            valid_until = cert.valid_until.strftime("%Y-%m-%d %H:%M")[:20].ljust(20)
            fingerprint = cert.sha256_fingerprint[:10]
            
            print(f"  │ {cn} │ {cert_type} │ {algo} │ {status} │ {valid_until} │ {fingerprint}..│")
            
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # CSR status
    print("\n📨 CSR Status:")
    
    by_status = {}
    for csr in pki.csrs.values():
        by_status[csr.status.value] = by_status.get(csr.status.value, 0) + 1
        
    for status, count in by_status.items():
        print(f"  {status}: {count}")
        
    # Key algorithms distribution
    print("\n🔐 Key Algorithms:")
    
    stats = pki.get_statistics()
    for algo, count in stats['certificates_by_algorithm'].items():
        bar = "█" * count + "░" * (20 - count)
        print(f"  {algo:12} [{bar}] {count}")
        
    # Revocation summary
    print("\n🚫 Revocation Summary:")
    
    by_reason = {}
    for entry in pki.revocation_entries.values():
        by_reason[entry.reason.value] = by_reason.get(entry.reason.value, 0) + 1
        
    for reason, count in by_reason.items():
        print(f"  {reason}: {count}")
        
    # Statistics
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Certificate Authorities: {stats['active_cas']}/{stats['total_cas']} active")
    print(f"  Total Certificates: {stats['total_certificates']}")
    print(f"    Valid: {stats['valid_certificates']}")
    print(f"    Revoked: {stats['revoked_certificates']}")
    print(f"  Key Pairs: {stats['total_key_pairs']}")
    print(f"  CSRs: {stats['pending_csrs']}/{stats['total_csrs']} pending")
    print(f"  Templates: {stats['total_templates']}")
    print(f"  CRLs: {stats['total_crls']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                        PKI Manager Platform                         │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Certificate Authorities:          {stats['active_cas']:>12} active              │")
    print(f"│ Total Certificates:               {stats['total_certificates']:>12}                     │")
    print(f"│ Valid Certificates:               {stats['valid_certificates']:>12}                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Revoked Certificates:             {stats['revoked_certificates']:>12}                     │")
    print(f"│ Pending CSRs:                     {stats['pending_csrs']:>12}                     │")
    print(f"│ Key Pairs Managed:                {stats['total_key_pairs']:>12}                     │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("PKI Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
