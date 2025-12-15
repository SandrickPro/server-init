#!/usr/bin/env python3
"""
Server Init - Iteration 339: Certificate Lifecycle Manager Platform
Платформа управления жизненным циклом сертификатов

Функционал:
- Certificate Generation - генерация сертификатов
- CSR Management - управление запросами на сертификаты
- Certificate Authority - центр сертификации
- Auto-renewal - автоматическое продление
- Certificate Inventory - инвентаризация сертификатов
- Expiration Monitoring - мониторинг истечения
- Chain Validation - валидация цепочки сертификатов
- Deployment Automation - автоматизация развертывания
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


class CertificateType(Enum):
    """Тип сертификата"""
    ROOT_CA = "root_ca"
    INTERMEDIATE_CA = "intermediate_ca"
    END_ENTITY = "end_entity"
    SERVER = "server"
    CLIENT = "client"
    CODE_SIGNING = "code_signing"
    EMAIL = "email"
    WILDCARD = "wildcard"


class CertificateStatus(Enum):
    """Статус сертификата"""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"


class KeyAlgorithm(Enum):
    """Алгоритм ключа"""
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ECDSA_P384 = "ecdsa_p384"
    ED25519 = "ed25519"


class ValidationMethod(Enum):
    """Метод валидации домена"""
    DNS = "dns"
    HTTP = "http"
    EMAIL = "email"
    MANUAL = "manual"


class RevocationReason(Enum):
    """Причина отзыва"""
    UNSPECIFIED = "unspecified"
    KEY_COMPROMISE = "key_compromise"
    CA_COMPROMISE = "ca_compromise"
    AFFILIATION_CHANGED = "affiliation_changed"
    SUPERSEDED = "superseded"
    CESSATION_OF_OPERATION = "cessation_of_operation"
    CERTIFICATE_HOLD = "certificate_hold"


class DeploymentTarget(Enum):
    """Цель развертывания"""
    KUBERNETES = "kubernetes"
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"
    WEB_SERVER = "web_server"
    APPLICATION = "application"


@dataclass
class CertificateAuthority:
    """Центр сертификации"""
    ca_id: str
    name: str
    
    # Type
    is_root: bool = True
    parent_ca_id: str = ""
    
    # Key
    key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_4096
    
    # Subject
    common_name: str = ""
    organization: str = ""
    country: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Constraints
    path_length: int = -1  # -1 = unlimited
    max_validity_days: int = 365
    
    # Certificate
    certificate_pem: str = ""
    private_key_hash: str = ""
    
    # Status
    is_active: bool = True
    
    # Statistics
    certificates_issued: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CSR:
    """Запрос на сертификат"""
    csr_id: str
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    locality: str = ""
    state: str = ""
    country: str = ""
    
    # SANs
    dns_names: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    
    # Key
    key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    key_size: int = 2048
    
    # CSR Data
    csr_pem: str = ""
    
    # Validation
    validation_method: ValidationMethod = ValidationMethod.DNS
    is_validated: bool = False
    validation_token: str = ""
    
    # Status
    status: str = "pending"  # pending, approved, rejected, completed
    
    # Requester
    requester_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None


@dataclass
class Certificate:
    """Сертификат"""
    cert_id: str
    name: str
    
    # Type
    cert_type: CertificateType = CertificateType.SERVER
    
    # Subject
    common_name: str = ""
    organization: str = ""
    organizational_unit: str = ""
    
    # SANs
    dns_names: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    
    # Issuer
    issuer_ca_id: str = ""
    issuer_common_name: str = ""
    
    # Key
    key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048
    public_key_hash: str = ""
    
    # Certificate data
    certificate_pem: str = ""
    chain_pem: str = ""
    
    # Serial
    serial_number: str = ""
    
    # Validity
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    validity_days: int = 365
    
    # Status
    status: CertificateStatus = CertificateStatus.PENDING
    
    # Revocation
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[RevocationReason] = None
    
    # Renewal
    auto_renew: bool = True
    renew_before_days: int = 30
    renewal_count: int = 0
    
    # Deployment
    deployment_targets: List[str] = field(default_factory=list)
    last_deployed: Optional[datetime] = None
    
    # Fingerprints
    sha256_fingerprint: str = ""
    sha1_fingerprint: str = ""
    
    # Owner
    owner_id: str = ""
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeploymentConfig:
    """Конфигурация развертывания"""
    config_id: str
    name: str
    
    # Target
    target_type: DeploymentTarget = DeploymentTarget.KUBERNETES
    target_id: str = ""
    
    # Kubernetes specifics
    namespace: str = ""
    secret_name: str = ""
    
    # Load balancer specifics
    lb_id: str = ""
    
    # Certificate
    certificate_id: str = ""
    
    # Auto-deployment
    auto_deploy: bool = True
    
    # Status
    last_deployment_status: str = ""
    last_deployed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RenewalJob:
    """Задание на продление"""
    job_id: str
    
    # Certificate
    certificate_id: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    
    # Result
    new_certificate_id: str = ""
    error_message: str = ""
    
    # Timestamps
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CertificateChain:
    """Цепочка сертификатов"""
    chain_id: str
    
    # Certificates (from leaf to root)
    certificate_ids: List[str] = field(default_factory=list)
    
    # Validation
    is_valid: bool = False
    validation_errors: List[str] = field(default_factory=list)
    
    # Timestamps
    validated_at: Optional[datetime] = None


@dataclass
class RevocationEntry:
    """Запись об отзыве"""
    entry_id: str
    
    # Certificate
    certificate_id: str = ""
    serial_number: str = ""
    
    # Reason
    reason: RevocationReason = RevocationReason.UNSPECIFIED
    
    # Revoked by
    revoked_by: str = ""
    
    # Timestamps
    revoked_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditLog:
    """Запись аудита"""
    log_id: str
    
    # Operation
    operation: str = ""
    
    # Target
    certificate_id: str = ""
    ca_id: str = ""
    
    # Principal
    principal_id: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class CertificateLifecycleManager:
    """Менеджер жизненного цикла сертификатов"""
    
    def __init__(self):
        self.cas: Dict[str, CertificateAuthority] = {}
        self.csrs: Dict[str, CSR] = {}
        self.certificates: Dict[str, Certificate] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        self.renewal_jobs: Dict[str, RenewalJob] = {}
        self.revocations: Dict[str, RevocationEntry] = {}
        self.audit_logs: List[AuditLog] = []
        
    def _generate_serial(self) -> str:
        """Генерация серийного номера"""
        return uuid.uuid4().hex.upper()[:32]
        
    def _generate_fingerprint(self, data: str, algorithm: str = "sha256") -> str:
        """Генерация fingerprint"""
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest().upper()
        elif algorithm == "sha1":
            return hashlib.sha1(data.encode()).hexdigest().upper()
        return ""
        
    def _generate_certificate_pem(self, cert: Certificate) -> str:
        """Симуляция генерации PEM"""
        return f"-----BEGIN CERTIFICATE-----\nMIID...simulated...{cert.cert_id}...\n-----END CERTIFICATE-----"
        
    async def create_ca(self, name: str,
                       common_name: str,
                       organization: str,
                       country: str,
                       is_root: bool = True,
                       parent_ca_id: str = "",
                       key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_4096,
                       validity_years: int = 10,
                       path_length: int = -1,
                       max_validity_days: int = 365) -> Optional[CertificateAuthority]:
        """Создание CA"""
        if not is_root and parent_ca_id and parent_ca_id not in self.cas:
            return None
            
        ca = CertificateAuthority(
            ca_id=f"ca_{uuid.uuid4().hex[:8]}",
            name=name,
            is_root=is_root,
            parent_ca_id=parent_ca_id,
            key_algorithm=key_algorithm,
            common_name=common_name,
            organization=organization,
            country=country,
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=validity_years * 365),
            path_length=path_length,
            max_validity_days=max_validity_days
        )
        
        # Generate CA certificate
        ca.certificate_pem = f"-----BEGIN CERTIFICATE-----\nCA...{ca.ca_id}...\n-----END CERTIFICATE-----"
        ca.private_key_hash = hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()
        
        self.cas[ca.ca_id] = ca
        
        # Audit log
        await self._log_audit("create_ca", "", ca.ca_id, "system")
        
        return ca
        
    async def create_csr(self, common_name: str,
                        dns_names: List[str],
                        organization: str = "",
                        key_algorithm: KeyAlgorithm = KeyAlgorithm.RSA_2048,
                        validation_method: ValidationMethod = ValidationMethod.DNS,
                        requester_id: str = "",
                        ip_addresses: List[str] = None,
                        email_addresses: List[str] = None) -> CSR:
        """Создание CSR"""
        csr = CSR(
            csr_id=f"csr_{uuid.uuid4().hex[:12]}",
            common_name=common_name,
            organization=organization,
            dns_names=dns_names,
            ip_addresses=ip_addresses or [],
            email_addresses=email_addresses or [],
            key_algorithm=key_algorithm,
            validation_method=validation_method,
            requester_id=requester_id,
            validation_token=uuid.uuid4().hex
        )
        
        # Generate CSR PEM
        csr.csr_pem = f"-----BEGIN CERTIFICATE REQUEST-----\nCSR...{csr.csr_id}...\n-----END CERTIFICATE REQUEST-----"
        
        self.csrs[csr.csr_id] = csr
        
        # Audit log
        await self._log_audit("create_csr", csr.csr_id, "", requester_id)
        
        return csr
        
    async def validate_csr(self, csr_id: str) -> bool:
        """Валидация CSR"""
        csr = self.csrs.get(csr_id)
        if not csr:
            return False
            
        # Simulate validation
        csr.is_validated = True
        return True
        
    async def approve_csr(self, csr_id: str, approver_id: str) -> bool:
        """Одобрение CSR"""
        csr = self.csrs.get(csr_id)
        if not csr or not csr.is_validated:
            return False
            
        csr.status = "approved"
        csr.approved_at = datetime.now()
        
        # Audit log
        await self._log_audit("approve_csr", csr_id, "", approver_id)
        
        return True
        
    async def issue_certificate(self, csr_id: str,
                               ca_id: str,
                               cert_type: CertificateType = CertificateType.SERVER,
                               validity_days: int = 365,
                               auto_renew: bool = True,
                               labels: Dict[str, str] = None,
                               owner_id: str = "") -> Optional[Certificate]:
        """Выпуск сертификата"""
        csr = self.csrs.get(csr_id)
        ca = self.cas.get(ca_id)
        
        if not csr or csr.status != "approved" or not ca or not ca.is_active:
            return None
            
        # Check validity constraints
        if validity_days > ca.max_validity_days:
            validity_days = ca.max_validity_days
            
        cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:12]}",
            name=csr.common_name,
            cert_type=cert_type,
            common_name=csr.common_name,
            organization=csr.organization,
            dns_names=csr.dns_names,
            ip_addresses=csr.ip_addresses,
            issuer_ca_id=ca_id,
            issuer_common_name=ca.common_name,
            key_algorithm=csr.key_algorithm,
            serial_number=self._generate_serial(),
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=validity_days),
            validity_days=validity_days,
            status=CertificateStatus.ACTIVE,
            auto_renew=auto_renew,
            owner_id=owner_id,
            labels=labels or {}
        )
        
        # Generate certificate
        cert.certificate_pem = self._generate_certificate_pem(cert)
        cert.public_key_hash = hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()
        cert.sha256_fingerprint = self._generate_fingerprint(cert.certificate_pem, "sha256")
        cert.sha1_fingerprint = self._generate_fingerprint(cert.certificate_pem, "sha1")
        
        # Generate chain
        cert.chain_pem = cert.certificate_pem + "\n" + ca.certificate_pem
        
        # Update CSR status
        csr.status = "completed"
        
        # Update CA stats
        ca.certificates_issued += 1
        
        self.certificates[cert.cert_id] = cert
        
        # Audit log
        await self._log_audit("issue_certificate", cert.cert_id, ca_id, owner_id)
        
        return cert
        
    async def renew_certificate(self, cert_id: str,
                               validity_days: int = None,
                               principal_id: str = "") -> Optional[Certificate]:
        """Продление сертификата"""
        old_cert = self.certificates.get(cert_id)
        if not old_cert or old_cert.status != CertificateStatus.ACTIVE:
            return None
            
        ca = self.cas.get(old_cert.issuer_ca_id)
        if not ca or not ca.is_active:
            return None
            
        # Create renewal job
        job = RenewalJob(
            job_id=f"renew_{uuid.uuid4().hex[:8]}",
            certificate_id=cert_id,
            status="in_progress",
            started_at=datetime.now()
        )
        
        # Create new certificate
        validity = validity_days or old_cert.validity_days
        
        new_cert = Certificate(
            cert_id=f"cert_{uuid.uuid4().hex[:12]}",
            name=old_cert.name,
            cert_type=old_cert.cert_type,
            common_name=old_cert.common_name,
            organization=old_cert.organization,
            dns_names=old_cert.dns_names.copy(),
            ip_addresses=old_cert.ip_addresses.copy(),
            issuer_ca_id=old_cert.issuer_ca_id,
            issuer_common_name=old_cert.issuer_common_name,
            key_algorithm=old_cert.key_algorithm,
            serial_number=self._generate_serial(),
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=validity),
            validity_days=validity,
            status=CertificateStatus.ACTIVE,
            auto_renew=old_cert.auto_renew,
            renewal_count=old_cert.renewal_count + 1,
            deployment_targets=old_cert.deployment_targets.copy(),
            owner_id=old_cert.owner_id,
            labels=old_cert.labels.copy()
        )
        
        # Generate new certificate
        new_cert.certificate_pem = self._generate_certificate_pem(new_cert)
        new_cert.public_key_hash = hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()
        new_cert.sha256_fingerprint = self._generate_fingerprint(new_cert.certificate_pem, "sha256")
        new_cert.sha1_fingerprint = self._generate_fingerprint(new_cert.certificate_pem, "sha1")
        new_cert.chain_pem = new_cert.certificate_pem + "\n" + ca.certificate_pem
        
        # Update old certificate status
        old_cert.status = CertificateStatus.EXPIRED
        
        # Update CA stats
        ca.certificates_issued += 1
        
        self.certificates[new_cert.cert_id] = new_cert
        
        # Update job
        job.status = "completed"
        job.new_certificate_id = new_cert.cert_id
        job.completed_at = datetime.now()
        self.renewal_jobs[job.job_id] = job
        
        # Audit log
        await self._log_audit("renew_certificate", new_cert.cert_id, ca.ca_id, principal_id)
        
        return new_cert
        
    async def revoke_certificate(self, cert_id: str,
                                reason: RevocationReason,
                                principal_id: str) -> bool:
        """Отзыв сертификата"""
        cert = self.certificates.get(cert_id)
        if not cert or cert.status in [CertificateStatus.REVOKED, CertificateStatus.EXPIRED]:
            return False
            
        cert.status = CertificateStatus.REVOKED
        cert.revoked_at = datetime.now()
        cert.revocation_reason = reason
        
        # Create revocation entry
        entry = RevocationEntry(
            entry_id=f"rev_{uuid.uuid4().hex[:8]}",
            certificate_id=cert_id,
            serial_number=cert.serial_number,
            reason=reason,
            revoked_by=principal_id
        )
        
        self.revocations[entry.entry_id] = entry
        
        # Audit log
        await self._log_audit("revoke_certificate", cert_id, "", principal_id)
        
        return True
        
    async def create_deployment_config(self, name: str,
                                      certificate_id: str,
                                      target_type: DeploymentTarget,
                                      target_id: str,
                                      namespace: str = "",
                                      secret_name: str = "",
                                      auto_deploy: bool = True) -> Optional[DeploymentConfig]:
        """Создание конфигурации развертывания"""
        cert = self.certificates.get(certificate_id)
        if not cert:
            return None
            
        config = DeploymentConfig(
            config_id=f"deploy_{uuid.uuid4().hex[:8]}",
            name=name,
            target_type=target_type,
            target_id=target_id,
            namespace=namespace,
            secret_name=secret_name,
            certificate_id=certificate_id,
            auto_deploy=auto_deploy
        )
        
        cert.deployment_targets.append(config.config_id)
        self.deployments[config.config_id] = config
        
        return config
        
    async def deploy_certificate(self, config_id: str,
                                principal_id: str) -> bool:
        """Развертывание сертификата"""
        config = self.deployments.get(config_id)
        if not config:
            return False
            
        cert = self.certificates.get(config.certificate_id)
        if not cert or cert.status != CertificateStatus.ACTIVE:
            config.last_deployment_status = "failed: certificate not active"
            return False
            
        # Simulate deployment
        config.last_deployment_status = "success"
        config.last_deployed_at = datetime.now()
        cert.last_deployed = datetime.now()
        
        # Audit log
        await self._log_audit("deploy_certificate", config.certificate_id, "", principal_id)
        
        return True
        
    async def validate_chain(self, cert_id: str) -> CertificateChain:
        """Валидация цепочки сертификатов"""
        cert = self.certificates.get(cert_id)
        
        chain = CertificateChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}"
        )
        
        if not cert:
            chain.validation_errors.append("Certificate not found")
            return chain
            
        # Build chain
        chain.certificate_ids.append(cert_id)
        
        # Follow issuer chain
        current_ca_id = cert.issuer_ca_id
        while current_ca_id:
            ca = self.cas.get(current_ca_id)
            if not ca:
                chain.validation_errors.append(f"CA {current_ca_id} not found")
                break
            chain.certificate_ids.append(ca.ca_id)
            current_ca_id = ca.parent_ca_id if not ca.is_root else ""
            
        # Validate
        errors = []
        now = datetime.now()
        
        # Check certificate validity
        if cert.status != CertificateStatus.ACTIVE:
            errors.append(f"Certificate status is {cert.status.value}")
        if cert.valid_until and cert.valid_until < now:
            errors.append("Certificate has expired")
        if cert.valid_from > now:
            errors.append("Certificate is not yet valid")
            
        chain.validation_errors = errors
        chain.is_valid = len(errors) == 0
        chain.validated_at = now
        
        return chain
        
    def get_expiring_certificates(self, days: int = 30) -> List[Certificate]:
        """Получение истекающих сертификатов"""
        threshold = datetime.now() + timedelta(days=days)
        result = []
        
        for cert in self.certificates.values():
            if cert.status != CertificateStatus.ACTIVE:
                continue
            if cert.valid_until and cert.valid_until <= threshold:
                result.append(cert)
                
        return sorted(result, key=lambda c: c.valid_until)
        
    def get_certificates_needing_renewal(self) -> List[Certificate]:
        """Получение сертификатов, требующих продления"""
        result = []
        now = datetime.now()
        
        for cert in self.certificates.values():
            if cert.status != CertificateStatus.ACTIVE:
                continue
            if not cert.auto_renew:
                continue
            if cert.valid_until:
                renew_date = cert.valid_until - timedelta(days=cert.renew_before_days)
                if renew_date <= now:
                    result.append(cert)
                    
        return result
        
    async def _log_audit(self, operation: str,
                        cert_id: str,
                        ca_id: str,
                        principal_id: str,
                        success: bool = True,
                        error: str = "",
                        details: Dict[str, Any] = None):
        """Запись в аудит"""
        log = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:12]}",
            operation=operation,
            certificate_id=cert_id,
            ca_id=ca_id,
            principal_id=principal_id,
            success=success,
            error_message=error,
            details=details or {}
        )
        
        self.audit_logs.append(log)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_cas = len(self.cas)
        active_cas = sum(1 for ca in self.cas.values() if ca.is_active)
        
        total_certs = len(self.certificates)
        active_certs = sum(1 for c in self.certificates.values() 
                         if c.status == CertificateStatus.ACTIVE)
        expired_certs = sum(1 for c in self.certificates.values() 
                          if c.status == CertificateStatus.EXPIRED)
        revoked_certs = sum(1 for c in self.certificates.values() 
                          if c.status == CertificateStatus.REVOKED)
        
        # By type
        by_type = {}
        for cert in self.certificates.values():
            t = cert.cert_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        total_csrs = len(self.csrs)
        pending_csrs = sum(1 for c in self.csrs.values() if c.status == "pending")
        
        total_deployments = len(self.deployments)
        
        expiring_30d = len(self.get_expiring_certificates(30))
        expiring_7d = len(self.get_expiring_certificates(7))
        needing_renewal = len(self.get_certificates_needing_renewal())
        
        total_revocations = len(self.revocations)
        
        return {
            "total_cas": total_cas,
            "active_cas": active_cas,
            "total_certificates": total_certs,
            "active_certificates": active_certs,
            "expired_certificates": expired_certs,
            "revoked_certificates": revoked_certs,
            "certificates_by_type": by_type,
            "total_csrs": total_csrs,
            "pending_csrs": pending_csrs,
            "total_deployments": total_deployments,
            "expiring_30_days": expiring_30d,
            "expiring_7_days": expiring_7d,
            "needing_renewal": needing_renewal,
            "total_revocations": total_revocations
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 339: Certificate Lifecycle Manager")
    print("=" * 60)
    
    clm = CertificateLifecycleManager()
    print("✓ Certificate Lifecycle Manager initialized")
    
    # Create Certificate Authorities
    print("\n🏛️ Creating Certificate Authorities...")
    
    # Root CA
    root_ca = await clm.create_ca(
        "Enterprise Root CA",
        "Enterprise Root CA",
        "ACME Corporation",
        "US",
        is_root=True,
        key_algorithm=KeyAlgorithm.RSA_4096,
        validity_years=20,
        path_length=2,
        max_validity_days=3650
    )
    print(f"  🏛️ {root_ca.name} (Root)")
    
    # Intermediate CAs
    intermediate_cas = []
    int_ca_data = [
        ("Infrastructure CA", "Infrastructure CA", 365),
        ("Services CA", "Services CA", 365),
        ("Users CA", "Users CA", 180)
    ]
    
    for name, cn, max_validity in int_ca_data:
        ca = await clm.create_ca(
            name, cn,
            "ACME Corporation",
            "US",
            is_root=False,
            parent_ca_id=root_ca.ca_id,
            key_algorithm=KeyAlgorithm.RSA_4096,
            validity_years=10,
            path_length=0,
            max_validity_days=max_validity
        )
        intermediate_cas.append(ca)
        print(f"  🏛️ {name} (Intermediate)")
        
    # Create CSRs and Issue Certificates
    print("\n📝 Creating CSRs and Issuing Certificates...")
    
    csr_data = [
        ("www.example.com", ["www.example.com", "example.com"], "Web Services", KeyAlgorithm.RSA_2048, 0, CertificateType.SERVER),
        ("api.example.com", ["api.example.com", "api-v2.example.com"], "API Services", KeyAlgorithm.ECDSA_P256, 1, CertificateType.SERVER),
        ("*.internal.example.com", ["*.internal.example.com"], "Internal Services", KeyAlgorithm.RSA_2048, 0, CertificateType.WILDCARD),
        ("mail.example.com", ["mail.example.com", "smtp.example.com", "imap.example.com"], "Email Services", KeyAlgorithm.RSA_2048, 0, CertificateType.SERVER),
        ("code-signing", [], "Development", KeyAlgorithm.RSA_4096, 1, CertificateType.CODE_SIGNING),
        ("db.example.com", ["db.example.com", "db-replica.example.com"], "Database", KeyAlgorithm.RSA_2048, 0, CertificateType.SERVER),
        ("vpn.example.com", ["vpn.example.com"], "Network", KeyAlgorithm.ECDSA_P384, 0, CertificateType.SERVER),
        ("auth.example.com", ["auth.example.com", "sso.example.com"], "Security", KeyAlgorithm.ECDSA_P256, 1, CertificateType.SERVER),
        ("cdn.example.com", ["cdn.example.com", "static.example.com"], "CDN", KeyAlgorithm.RSA_2048, 0, CertificateType.SERVER),
        ("k8s-ingress", ["*.apps.example.com"], "Kubernetes", KeyAlgorithm.RSA_2048, 0, CertificateType.WILDCARD)
    ]
    
    certificates = []
    for cn, dns_names, org, algo, ca_idx, cert_type in csr_data:
        csr = await clm.create_csr(
            cn, dns_names, org, algo,
            ValidationMethod.DNS,
            "admin"
        )
        
        await clm.validate_csr(csr.csr_id)
        await clm.approve_csr(csr.csr_id, "admin")
        
        cert = await clm.issue_certificate(
            csr.csr_id,
            intermediate_cas[ca_idx].ca_id,
            cert_type,
            validity_days=random.choice([90, 180, 365]),
            auto_renew=True,
            labels={"env": random.choice(["production", "staging", "development"])},
            owner_id="admin"
        )
        
        if cert:
            certificates.append(cert)
            print(f"  📜 {cn}")
            
    # Create Deployment Configs
    print("\n🚀 Creating Deployment Configurations...")
    
    deployments_data = [
        (certificates[0].cert_id, "Production Web", DeploymentTarget.LOAD_BALANCER, "lb-prod-1"),
        (certificates[1].cert_id, "API Gateway", DeploymentTarget.APPLICATION, "api-gw-1"),
        (certificates[2].cert_id, "K8s Internal", DeploymentTarget.KUBERNETES, "k8s-cluster-1"),
        (certificates[3].cert_id, "Mail Server", DeploymentTarget.WEB_SERVER, "mail-server-1"),
        (certificates[8].cert_id, "CDN Edge", DeploymentTarget.CDN, "cdn-edge-1"),
        (certificates[9].cert_id, "K8s Ingress", DeploymentTarget.KUBERNETES, "k8s-cluster-1")
    ]
    
    deployments = []
    for cert_id, name, target, target_id in deployments_data:
        config = await clm.create_deployment_config(
            name, cert_id, target, target_id,
            namespace="production" if target == DeploymentTarget.KUBERNETES else "",
            secret_name=f"tls-{name.lower().replace(' ', '-')}" if target == DeploymentTarget.KUBERNETES else "",
            auto_deploy=True
        )
        if config:
            deployments.append(config)
            # Deploy
            await clm.deploy_certificate(config.config_id, "admin")
            print(f"  🚀 {name} → {target.value}")
            
    # Simulate certificate expiration
    print("\n⏰ Simulating Certificate Expiration...")
    
    # Set some certificates to expire soon
    for cert in certificates[6:8]:
        cert.valid_until = datetime.now() + timedelta(days=random.randint(5, 25))
        
    expiring = clm.get_expiring_certificates(30)
    print(f"  ⏰ {len(expiring)} certificates expiring in 30 days")
    
    # Renew a certificate
    print("\n🔄 Renewing Certificates...")
    
    if expiring:
        new_cert = await clm.renew_certificate(
            expiring[0].cert_id,
            validity_days=365,
            principal_id="admin"
        )
        if new_cert:
            certificates.append(new_cert)
            print(f"  🔄 Renewed: {new_cert.common_name}")
            
    # Revoke a certificate
    print("\n❌ Revoking Certificate...")
    
    revoked = await clm.revoke_certificate(
        certificates[4].cert_id,
        RevocationReason.SUPERSEDED,
        "admin"
    )
    if revoked:
        print(f"  ❌ Revoked: {certificates[4].common_name}")
        
    # Validate chains
    print("\n🔗 Validating Certificate Chains...")
    
    for cert in certificates[:5]:
        chain = await clm.validate_chain(cert.cert_id)
        status = "✓ Valid" if chain.is_valid else f"✗ Invalid: {', '.join(chain.validation_errors)}"
        print(f"  🔗 {cert.common_name}: {status}")
        
    # Certificate Authorities
    print("\n🏛️ Certificate Authorities:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Type          │ Algorithm  │ Organization        │ Valid Until          │ Max Validity │ Issued │ Status                                                                         │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    all_cas = [root_ca] + intermediate_cas
    for ca in all_cas:
        name = ca.name[:25].ljust(25)
        ca_type = "Root" if ca.is_root else "Intermediate"
        ca_type = ca_type[:13].ljust(13)
        algo = ca.key_algorithm.value[:10].ljust(10)
        org = ca.organization[:19].ljust(19)
        valid = ca.valid_until.strftime("%Y-%m-%d") if ca.valid_until else "N/A"
        valid = valid[:20].ljust(20)
        max_val = f"{ca.max_validity_days}d".ljust(12)
        issued = str(ca.certificates_issued).ljust(6)
        status = "✓ Active" if ca.is_active else "○ Inactive"
        status = status[:80].ljust(80)
        
        print(f"  │ {name} │ {ca_type} │ {algo} │ {org} │ {valid} │ {max_val} │ {issued} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Certificates
    print("\n📜 Certificates:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Common Name                │ Type           │ Algorithm     │ Valid Until          │ Auto-Renew │ Deployed │ Status                                                                                                                      │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cert in certificates:
        cn = cert.common_name[:26].ljust(26)
        ctype = cert.cert_type.value[:14].ljust(14)
        algo = cert.key_algorithm.value[:13].ljust(13)
        valid = cert.valid_until.strftime("%Y-%m-%d") if cert.valid_until else "N/A"
        valid = valid[:20].ljust(20)
        auto = "✓" if cert.auto_renew else "✗"
        auto = auto.ljust(10)
        deployed = "✓" if cert.last_deployed else "✗"
        deployed = deployed.ljust(8)
        
        status_icon = {"active": "✓", "expired": "⏰", "revoked": "✗", "pending": "⌛"}.get(cert.status.value, "?")
        status = f"{status_icon} {cert.status.value}"[:121].ljust(121)
        
        print(f"  │ {cn} │ {ctype} │ {algo} │ {valid} │ {auto} │ {deployed} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Certificate Details
    print("\n🔍 Certificate Details (Sample):")
    
    sample_cert = certificates[0]
    print(f"\n  Certificate: {sample_cert.common_name}")
    print(f"  ├─ Serial: {sample_cert.serial_number[:20]}...")
    print(f"  ├─ Type: {sample_cert.cert_type.value}")
    print(f"  ├─ Algorithm: {sample_cert.key_algorithm.value}")
    print(f"  ├─ Issuer: {sample_cert.issuer_common_name}")
    print(f"  ├─ Valid From: {sample_cert.valid_from.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  ├─ Valid Until: {sample_cert.valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  ├─ SANs: {', '.join(sample_cert.dns_names)}")
    print(f"  ├─ SHA256: {sample_cert.sha256_fingerprint[:32]}...")
    print(f"  └─ SHA1: {sample_cert.sha1_fingerprint[:32]}...")
    
    # Deployment Configurations
    print("\n🚀 Deployment Configurations:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Target Type     │ Target ID          │ Auto-Deploy │ Last Status │ Last Deployed                                                                            │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for deploy in deployments:
        name = deploy.name[:23].ljust(23)
        target = deploy.target_type.value[:15].ljust(15)
        target_id = deploy.target_id[:18].ljust(18)
        auto = "✓" if deploy.auto_deploy else "✗"
        auto = auto.ljust(11)
        status = deploy.last_deployment_status[:11].ljust(11)
        last = deploy.last_deployed_at.strftime("%Y-%m-%d %H:%M") if deploy.last_deployed_at else "Never"
        last = last[:90].ljust(90)
        
        print(f"  │ {name} │ {target} │ {target_id} │ {auto} │ {status} │ {last} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Expiring Certificates
    expiring_certs = clm.get_expiring_certificates(30)
    if expiring_certs:
        print("\n⚠️ Expiring Soon (30 days):")
        
        print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Common Name                │ Valid Until          │ Days Left │ Auto-Renew │ Status                                │")
        print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for cert in expiring_certs:
            cn = cert.common_name[:26].ljust(26)
            valid = cert.valid_until.strftime("%Y-%m-%d") if cert.valid_until else "N/A"
            valid = valid[:20].ljust(20)
            days_left = (cert.valid_until - datetime.now()).days if cert.valid_until else 0
            days = str(days_left).ljust(9)
            auto = "✓" if cert.auto_renew else "✗"
            auto = auto.ljust(10)
            status = "⚠️ Expiring soon"[:39].ljust(39)
            
            print(f"  │ {cn} │ {valid} │ {days} │ {auto} │ {status} │")
            
        print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
    # Audit Logs
    print("\n📋 Recent Audit Logs:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Operation             │ Certificate                │ CA                        │ Principal      │ Timestamp            │ Status                                                                         │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for log in clm.audit_logs[-12:]:
        operation = log.operation[:21].ljust(21)
        cert_id = log.certificate_id[:26].ljust(26)
        ca_id = log.ca_id[:25].ljust(25)
        principal = log.principal_id[:14].ljust(14)
        timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        
        status_icon = "✓" if log.success else "✗"
        status = f"{status_icon} {'Success' if log.success else log.error_message}"[:80].ljust(80)
        
        print(f"  │ {operation} │ {cert_id} │ {ca_id} │ {principal} │ {timestamp} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = clm.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Certificate Authorities: {stats['active_cas']}/{stats['total_cas']} active")
    print(f"  Total Certificates: {stats['total_certificates']}")
    print(f"    Active: {stats['active_certificates']}")
    print(f"    Expired: {stats['expired_certificates']}")
    print(f"    Revoked: {stats['revoked_certificates']}")
    print(f"  CSRs: {stats['pending_csrs']}/{stats['total_csrs']} pending")
    print(f"  Deployments: {stats['total_deployments']}")
    print(f"  Expiring (30d): {stats['expiring_30_days']}")
    print(f"  Expiring (7d): {stats['expiring_7_days']}")
    print(f"  Needing Renewal: {stats['needing_renewal']}")
    
    print("\n  Certificates by Type:")
    for ctype, count in stats['certificates_by_type'].items():
        print(f"    {ctype}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                 Certificate Lifecycle Manager                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active CAs:                   {stats['active_cas']:>12}                      │")
    print(f"│ Total Certificates:           {stats['total_certificates']:>12}                      │")
    print(f"│ Active Certificates:          {stats['active_certificates']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Deployments:                  {stats['total_deployments']:>12}                      │")
    print(f"│ Expiring (30 days):           {stats['expiring_30_days']:>12}                      │")
    print(f"│ Needing Renewal:              {stats['needing_renewal']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Certificate Lifecycle Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
