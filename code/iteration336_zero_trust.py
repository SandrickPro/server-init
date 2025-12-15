#!/usr/bin/env python3
"""
Server Init - Iteration 336: Zero Trust Security Platform
Платформа безопасности Zero Trust

Функционал:
- Identity Verification - верификация идентичности
- Device Trust - доверие устройствам
- Network Micro-segmentation - микросегментация сети
- Continuous Verification - непрерывная проверка
- Least Privilege Access - минимальные привилегии
- Risk-based Authentication - аутентификация на основе риска
- Policy Engine - движок политик
- Threat Detection - обнаружение угроз
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class TrustScore(Enum):
    """Уровень доверия"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNTRUSTED = "untrusted"


class DeviceCompliance(Enum):
    """Соответствие устройства"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"
    NEEDS_UPDATE = "needs_update"


class RiskLevel(Enum):
    """Уровень риска"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class AccessDecision(Enum):
    """Решение о доступе"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_MFA = "require_mfa"
    REQUIRE_APPROVAL = "require_approval"
    STEP_UP = "step_up"


class SegmentationType(Enum):
    """Тип сегментации"""
    APPLICATION = "application"
    NETWORK = "network"
    DATA = "data"
    IDENTITY = "identity"


class ThreatType(Enum):
    """Тип угрозы"""
    ANOMALOUS_LOGIN = "anomalous_login"
    IMPOSSIBLE_TRAVEL = "impossible_travel"
    BRUTE_FORCE = "brute_force"
    COMPROMISED_CREDENTIAL = "compromised_credential"
    MALWARE = "malware"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class PolicyAction(Enum):
    """Действие политики"""
    ALLOW = "allow"
    DENY = "deny"
    MONITOR = "monitor"
    ALERT = "alert"
    QUARANTINE = "quarantine"


@dataclass
class Identity:
    """Идентичность"""
    identity_id: str
    
    # User info
    username: str = ""
    email: str = ""
    display_name: str = ""
    
    # Type
    identity_type: str = "user"  # user, service, device
    
    # Trust
    trust_score: TrustScore = TrustScore.MEDIUM
    trust_value: float = 50.0  # 0-100
    
    # Verification
    verified: bool = False
    verification_methods: List[str] = field(default_factory=list)
    last_verification: Optional[datetime] = None
    
    # Risk
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: List[str] = field(default_factory=list)
    
    # Devices
    registered_device_ids: List[str] = field(default_factory=list)
    
    # Access
    permissions: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None


@dataclass
class Device:
    """Устройство"""
    device_id: str
    name: str
    
    # Owner
    owner_identity_id: str = ""
    
    # Type
    device_type: str = "workstation"  # workstation, mobile, server, iot
    
    # Platform
    platform: str = ""  # windows, macos, linux, ios, android
    os_version: str = ""
    
    # Trust
    trust_score: TrustScore = TrustScore.MEDIUM
    trust_value: float = 50.0
    
    # Compliance
    compliance_status: DeviceCompliance = DeviceCompliance.UNKNOWN
    compliance_checks: Dict[str, bool] = field(default_factory=dict)
    
    # Security
    encryption_enabled: bool = False
    antivirus_enabled: bool = False
    firewall_enabled: bool = False
    last_scan: Optional[datetime] = None
    
    # Network
    ip_address: str = ""
    mac_address: str = ""
    network_zone: str = ""
    
    # Certificate
    certificate_id: str = ""
    certificate_expires: Optional[datetime] = None
    
    # Status
    is_registered: bool = True
    is_online: bool = False
    last_seen: Optional[datetime] = None
    
    # Timestamps
    enrolled_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkSegment:
    """Сетевой сегмент"""
    segment_id: str
    name: str
    
    # Type
    segment_type: SegmentationType = SegmentationType.NETWORK
    
    # Network
    cidr: str = ""
    vlan_id: int = 0
    
    # Trust
    trust_level: TrustScore = TrustScore.MEDIUM
    
    # Access control
    allowed_identities: List[str] = field(default_factory=list)
    allowed_devices: List[str] = field(default_factory=list)
    
    # Resources
    resource_ids: List[str] = field(default_factory=list)
    
    # Isolation
    isolation_level: str = "standard"  # none, standard, strict, complete
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Resource:
    """Защищаемый ресурс"""
    resource_id: str
    name: str
    
    # Type
    resource_type: str = "application"  # application, data, service, api
    
    # Location
    url: str = ""
    host: str = ""
    port: int = 0
    
    # Segment
    segment_id: str = ""
    
    # Sensitivity
    sensitivity_level: str = "internal"  # public, internal, confidential, restricted
    data_classification: str = ""
    
    # Access requirements
    min_trust_score: TrustScore = TrustScore.MEDIUM
    require_mfa: bool = False
    require_device_compliance: bool = True
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ZeroTrustPolicy:
    """Политика Zero Trust"""
    policy_id: str
    name: str
    
    # Scope
    identity_groups: List[str] = field(default_factory=list)
    device_types: List[str] = field(default_factory=list)
    resource_ids: List[str] = field(default_factory=list)
    segment_ids: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Requirements
    min_trust_score: float = 50.0
    require_mfa: bool = False
    require_device_compliance: bool = True
    require_network_compliance: bool = False
    
    # Time restrictions
    allowed_hours: List[int] = field(default_factory=list)
    allowed_days: List[int] = field(default_factory=list)
    
    # Geo restrictions
    allowed_countries: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    
    # Action
    action: PolicyAction = PolicyAction.ALLOW
    
    # Priority
    priority: int = 0
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessRequest:
    """Запрос на доступ"""
    request_id: str
    
    # Requester
    identity_id: str = ""
    device_id: str = ""
    
    # Target
    resource_id: str = ""
    segment_id: str = ""
    
    # Context
    source_ip: str = ""
    location: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Risk assessment
    risk_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    
    # Decision
    decision: AccessDecision = AccessDecision.DENY
    decision_reason: str = ""
    policy_id: str = ""
    
    # Status
    is_processed: bool = False
    
    # Timestamps
    processed_at: Optional[datetime] = None


@dataclass
class ThreatIndicator:
    """Индикатор угрозы"""
    indicator_id: str
    
    # Type
    threat_type: ThreatType = ThreatType.ANOMALOUS_LOGIN
    
    # Target
    identity_id: str = ""
    device_id: str = ""
    
    # Details
    description: str = ""
    severity: RiskLevel = RiskLevel.MEDIUM
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    is_resolved: bool = False
    
    # Response
    response_action: str = ""
    responded_by: str = ""
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class ContinuousVerification:
    """Непрерывная верификация"""
    verification_id: str
    
    # Session
    session_id: str = ""
    identity_id: str = ""
    device_id: str = ""
    
    # Checks
    checks_performed: List[str] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0
    
    # Trust
    current_trust_score: float = 0.0
    trust_delta: float = 0.0
    
    # Anomalies
    anomalies_detected: List[str] = field(default_factory=list)
    
    # Decision
    continue_session: bool = True
    require_reauthentication: bool = False
    
    # Timestamps
    verified_at: datetime = field(default_factory=datetime.now)


@dataclass
class MicroSegmentationRule:
    """Правило микросегментации"""
    rule_id: str
    name: str
    
    # Source
    source_segment_id: str = ""
    source_identities: List[str] = field(default_factory=list)
    
    # Destination
    dest_segment_id: str = ""
    dest_resources: List[str] = field(default_factory=list)
    
    # Ports/Protocols
    allowed_ports: List[int] = field(default_factory=list)
    allowed_protocols: List[str] = field(default_factory=list)
    
    # Action
    action: PolicyAction = PolicyAction.ALLOW
    
    # Logging
    log_traffic: bool = True
    
    # Status
    is_enabled: bool = True
    
    # Stats
    matches_count: int = 0
    last_matched: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RiskAssessment:
    """Оценка риска"""
    assessment_id: str
    
    # Target
    identity_id: str = ""
    device_id: str = ""
    session_id: str = ""
    
    # Risk factors
    risk_factors: Dict[str, float] = field(default_factory=dict)
    
    # Score
    overall_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Timestamp
    assessed_at: datetime = field(default_factory=datetime.now)


class ZeroTrustManager:
    """Менеджер Zero Trust"""
    
    def __init__(self):
        self.identities: Dict[str, Identity] = {}
        self.devices: Dict[str, Device] = {}
        self.segments: Dict[str, NetworkSegment] = {}
        self.resources: Dict[str, Resource] = {}
        self.policies: Dict[str, ZeroTrustPolicy] = {}
        self.access_requests: Dict[str, AccessRequest] = {}
        self.threats: Dict[str, ThreatIndicator] = {}
        self.verifications: Dict[str, ContinuousVerification] = {}
        self.segmentation_rules: Dict[str, MicroSegmentationRule] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        
    async def register_identity(self, username: str,
                               email: str,
                               display_name: str,
                               identity_type: str = "user",
                               groups: List[str] = None) -> Identity:
        """Регистрация идентичности"""
        identity = Identity(
            identity_id=f"id_{uuid.uuid4().hex[:8]}",
            username=username,
            email=email,
            display_name=display_name,
            identity_type=identity_type,
            groups=groups or []
        )
        
        self.identities[identity.identity_id] = identity
        return identity
        
    async def register_device(self, name: str,
                             owner_id: str,
                             device_type: str,
                             platform: str,
                             os_version: str) -> Optional[Device]:
        """Регистрация устройства"""
        owner = self.identities.get(owner_id)
        if not owner:
            return None
            
        device = Device(
            device_id=f"dev_{uuid.uuid4().hex[:8]}",
            name=name,
            owner_identity_id=owner_id,
            device_type=device_type,
            platform=platform,
            os_version=os_version
        )
        
        owner.registered_device_ids.append(device.device_id)
        self.devices[device.device_id] = device
        return device
        
    async def update_device_compliance(self, device_id: str,
                                      encryption: bool,
                                      antivirus: bool,
                                      firewall: bool,
                                      additional_checks: Dict[str, bool] = None) -> bool:
        """Обновление соответствия устройства"""
        device = self.devices.get(device_id)
        if not device:
            return False
            
        device.encryption_enabled = encryption
        device.antivirus_enabled = antivirus
        device.firewall_enabled = firewall
        device.last_scan = datetime.now()
        
        # Compliance checks
        checks = {
            "encryption": encryption,
            "antivirus": antivirus,
            "firewall": firewall
        }
        if additional_checks:
            checks.update(additional_checks)
            
        device.compliance_checks = checks
        
        # Determine compliance status
        all_passed = all(checks.values())
        any_failed = any(not v for v in checks.values())
        
        if all_passed:
            device.compliance_status = DeviceCompliance.COMPLIANT
            device.trust_score = TrustScore.HIGH
            device.trust_value = 80.0
        elif any_failed:
            device.compliance_status = DeviceCompliance.NON_COMPLIANT
            device.trust_score = TrustScore.LOW
            device.trust_value = 30.0
        else:
            device.compliance_status = DeviceCompliance.NEEDS_UPDATE
            device.trust_score = TrustScore.MEDIUM
            device.trust_value = 50.0
            
        return True
        
    async def create_segment(self, name: str,
                            segment_type: SegmentationType,
                            cidr: str,
                            trust_level: TrustScore = TrustScore.MEDIUM,
                            isolation_level: str = "standard") -> NetworkSegment:
        """Создание сетевого сегмента"""
        segment = NetworkSegment(
            segment_id=f"seg_{uuid.uuid4().hex[:8]}",
            name=name,
            segment_type=segment_type,
            cidr=cidr,
            trust_level=trust_level,
            isolation_level=isolation_level
        )
        
        self.segments[segment.segment_id] = segment
        return segment
        
    async def register_resource(self, name: str,
                               resource_type: str,
                               url: str,
                               segment_id: str,
                               sensitivity_level: str = "internal",
                               require_mfa: bool = False) -> Optional[Resource]:
        """Регистрация ресурса"""
        segment = self.segments.get(segment_id)
        if not segment:
            return None
            
        resource = Resource(
            resource_id=f"res_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_type=resource_type,
            url=url,
            segment_id=segment_id,
            sensitivity_level=sensitivity_level,
            require_mfa=require_mfa
        )
        
        segment.resource_ids.append(resource.resource_id)
        self.resources[resource.resource_id] = resource
        return resource
        
    async def create_policy(self, name: str,
                           identity_groups: List[str],
                           resource_ids: List[str],
                           min_trust_score: float = 50.0,
                           require_mfa: bool = False,
                           require_device_compliance: bool = True,
                           action: PolicyAction = PolicyAction.ALLOW,
                           priority: int = 0) -> ZeroTrustPolicy:
        """Создание политики Zero Trust"""
        policy = ZeroTrustPolicy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            identity_groups=identity_groups,
            resource_ids=resource_ids,
            min_trust_score=min_trust_score,
            require_mfa=require_mfa,
            require_device_compliance=require_device_compliance,
            action=action,
            priority=priority
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def create_segmentation_rule(self, name: str,
                                      source_segment_id: str,
                                      dest_segment_id: str,
                                      allowed_ports: List[int],
                                      allowed_protocols: List[str],
                                      action: PolicyAction = PolicyAction.ALLOW) -> Optional[MicroSegmentationRule]:
        """Создание правила микросегментации"""
        if source_segment_id not in self.segments or dest_segment_id not in self.segments:
            return None
            
        rule = MicroSegmentationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=name,
            source_segment_id=source_segment_id,
            dest_segment_id=dest_segment_id,
            allowed_ports=allowed_ports,
            allowed_protocols=allowed_protocols,
            action=action
        )
        
        self.segmentation_rules[rule.rule_id] = rule
        return rule
        
    async def process_access_request(self, identity_id: str,
                                    device_id: str,
                                    resource_id: str,
                                    source_ip: str,
                                    location: str = "") -> AccessRequest:
        """Обработка запроса на доступ"""
        request = AccessRequest(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            identity_id=identity_id,
            device_id=device_id,
            resource_id=resource_id,
            source_ip=source_ip,
            location=location
        )
        
        identity = self.identities.get(identity_id)
        device = self.devices.get(device_id)
        resource = self.resources.get(resource_id)
        
        if not identity or not device or not resource:
            request.decision = AccessDecision.DENY
            request.decision_reason = "Invalid identity, device, or resource"
            request.is_processed = True
            request.processed_at = datetime.now()
            self.access_requests[request.request_id] = request
            return request
            
        # Risk assessment
        risk = await self._assess_risk(identity, device, source_ip, location)
        request.risk_score = risk.overall_risk_score
        request.risk_factors = list(risk.risk_factors.keys())
        
        # Find applicable policies
        applicable_policies = []
        for policy in self.policies.values():
            if not policy.is_enabled:
                continue
            if policy.resource_ids and resource_id not in policy.resource_ids:
                continue
            if policy.identity_groups and not any(g in identity.groups for g in policy.identity_groups):
                continue
            applicable_policies.append(policy)
            
        # Sort by priority
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        # Evaluate policies
        decision = AccessDecision.DENY
        decision_reason = "No applicable policy"
        policy_id = ""
        
        for policy in applicable_policies:
            # Check trust score
            combined_trust = (identity.trust_value + device.trust_value) / 2
            if combined_trust < policy.min_trust_score:
                continue
                
            # Check device compliance
            if policy.require_device_compliance and device.compliance_status != DeviceCompliance.COMPLIANT:
                decision = AccessDecision.DENY
                decision_reason = "Device not compliant"
                policy_id = policy.policy_id
                break
                
            # Check MFA
            if policy.require_mfa:
                decision = AccessDecision.REQUIRE_MFA
                decision_reason = "MFA required"
                policy_id = policy.policy_id
                break
                
            # Check risk
            if risk.overall_risk_score > 70:
                decision = AccessDecision.REQUIRE_MFA
                decision_reason = "High risk detected"
                policy_id = policy.policy_id
                break
                
            # Allow
            if policy.action == PolicyAction.ALLOW:
                decision = AccessDecision.ALLOW
                decision_reason = "Access granted by policy"
                policy_id = policy.policy_id
                break
                
        request.decision = decision
        request.decision_reason = decision_reason
        request.policy_id = policy_id
        request.is_processed = True
        request.processed_at = datetime.now()
        
        # Update identity activity
        identity.last_activity = datetime.now()
        
        self.access_requests[request.request_id] = request
        return request
        
    async def _assess_risk(self, identity: Identity,
                          device: Device,
                          source_ip: str,
                          location: str) -> RiskAssessment:
        """Оценка риска"""
        risk_factors = {}
        
        # Identity risk factors
        if identity.trust_value < 50:
            risk_factors["low_identity_trust"] = 20.0
        if not identity.verified:
            risk_factors["unverified_identity"] = 15.0
        if identity.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            risk_factors["high_risk_identity"] = 30.0
            
        # Device risk factors
        if device.compliance_status != DeviceCompliance.COMPLIANT:
            risk_factors["non_compliant_device"] = 25.0
        if device.trust_value < 50:
            risk_factors["low_device_trust"] = 20.0
        if not device.encryption_enabled:
            risk_factors["no_encryption"] = 15.0
        if not device.antivirus_enabled:
            risk_factors["no_antivirus"] = 10.0
            
        # Network risk factors
        if device.network_zone == "untrusted":
            risk_factors["untrusted_network"] = 20.0
            
        # Location risk factors  
        if location and location not in ["US", "UK", "DE", "CA"]:
            risk_factors["unusual_location"] = 15.0
            
        # Calculate overall score
        overall_score = sum(risk_factors.values())
        overall_score = min(100, overall_score)
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif overall_score >= 60:
            risk_level = RiskLevel.HIGH
        elif overall_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif overall_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
            
        assessment = RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            identity_id=identity.identity_id,
            device_id=device.device_id,
            risk_factors=risk_factors,
            overall_risk_score=overall_score,
            risk_level=risk_level
        )
        
        # Update identity risk
        identity.risk_level = risk_level
        identity.risk_factors = list(risk_factors.keys())
        
        self.risk_assessments[assessment.assessment_id] = assessment
        return assessment
        
    async def detect_threat(self, threat_type: ThreatType,
                           identity_id: str = "",
                           device_id: str = "",
                           description: str = "",
                           severity: RiskLevel = RiskLevel.MEDIUM,
                           evidence: Dict[str, Any] = None) -> ThreatIndicator:
        """Обнаружение угрозы"""
        threat = ThreatIndicator(
            indicator_id=f"threat_{uuid.uuid4().hex[:8]}",
            threat_type=threat_type,
            identity_id=identity_id,
            device_id=device_id,
            description=description,
            severity=severity,
            evidence=evidence or {}
        )
        
        # Update identity/device trust if affected
        if identity_id:
            identity = self.identities.get(identity_id)
            if identity:
                if severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    identity.trust_score = TrustScore.LOW
                    identity.trust_value = max(0, identity.trust_value - 30)
                else:
                    identity.trust_value = max(0, identity.trust_value - 10)
                    
        if device_id:
            device = self.devices.get(device_id)
            if device:
                if severity in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    device.trust_score = TrustScore.LOW
                    device.trust_value = max(0, device.trust_value - 30)
                else:
                    device.trust_value = max(0, device.trust_value - 10)
                    
        self.threats[threat.indicator_id] = threat
        return threat
        
    async def continuous_verify(self, session_id: str,
                               identity_id: str,
                               device_id: str) -> ContinuousVerification:
        """Непрерывная верификация"""
        identity = self.identities.get(identity_id)
        device = self.devices.get(device_id)
        
        verification = ContinuousVerification(
            verification_id=f"cv_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            identity_id=identity_id,
            device_id=device_id
        )
        
        checks = []
        passed = 0
        failed = 0
        anomalies = []
        
        # Identity checks
        if identity:
            checks.append("identity_active")
            if identity.is_active:
                passed += 1
            else:
                failed += 1
                anomalies.append("identity_inactive")
                
            checks.append("identity_trust")
            if identity.trust_value >= 30:
                passed += 1
            else:
                failed += 1
                anomalies.append("low_identity_trust")
                
        # Device checks
        if device:
            checks.append("device_online")
            if device.is_online:
                passed += 1
            else:
                failed += 1
                
            checks.append("device_compliance")
            if device.compliance_status == DeviceCompliance.COMPLIANT:
                passed += 1
            else:
                failed += 1
                anomalies.append("device_non_compliant")
                
            checks.append("device_trust")
            if device.trust_value >= 30:
                passed += 1
            else:
                failed += 1
                anomalies.append("low_device_trust")
                
        verification.checks_performed = checks
        verification.checks_passed = passed
        verification.checks_failed = failed
        verification.anomalies_detected = anomalies
        
        # Calculate trust delta
        if identity and device:
            current_trust = (identity.trust_value + device.trust_value) / 2
            verification.current_trust_score = current_trust
            
        # Decision
        if failed > 2 or anomalies:
            verification.continue_session = False
            verification.require_reauthentication = True
            
        self.verifications[verification.verification_id] = verification
        return verification
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_identities = len(self.identities)
        active_identities = sum(1 for i in self.identities.values() if i.is_active)
        verified_identities = sum(1 for i in self.identities.values() if i.verified)
        
        total_devices = len(self.devices)
        compliant_devices = sum(1 for d in self.devices.values() 
                               if d.compliance_status == DeviceCompliance.COMPLIANT)
        
        total_segments = len(self.segments)
        total_resources = len(self.resources)
        
        total_policies = len(self.policies)
        enabled_policies = sum(1 for p in self.policies.values() if p.is_enabled)
        
        total_requests = len(self.access_requests)
        allowed_requests = sum(1 for r in self.access_requests.values() 
                              if r.decision == AccessDecision.ALLOW)
        denied_requests = sum(1 for r in self.access_requests.values() 
                             if r.decision == AccessDecision.DENY)
        
        total_threats = len(self.threats)
        active_threats = sum(1 for t in self.threats.values() if t.is_active and not t.is_resolved)
        
        total_rules = len(self.segmentation_rules)
        
        return {
            "total_identities": total_identities,
            "active_identities": active_identities,
            "verified_identities": verified_identities,
            "total_devices": total_devices,
            "compliant_devices": compliant_devices,
            "total_segments": total_segments,
            "total_resources": total_resources,
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "total_access_requests": total_requests,
            "allowed_requests": allowed_requests,
            "denied_requests": denied_requests,
            "total_threats": total_threats,
            "active_threats": active_threats,
            "total_segmentation_rules": total_rules
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 336: Zero Trust Security Platform")
    print("=" * 60)
    
    zt = ZeroTrustManager()
    print("✓ Zero Trust Manager created")
    
    # Register Identities
    print("\n👤 Registering Identities...")
    
    identities_data = [
        ("john.doe", "john.doe@example.com", "John Doe", "user", ["developers", "engineering"]),
        ("jane.smith", "jane.smith@example.com", "Jane Smith", "user", ["admins", "security"]),
        ("bob.wilson", "bob.wilson@example.com", "Bob Wilson", "user", ["analysts", "finance"]),
        ("alice.johnson", "alice.johnson@example.com", "Alice Johnson", "user", ["developers", "qa"]),
        ("charlie.brown", "charlie.brown@example.com", "Charlie Brown", "user", ["support"]),
        ("svc-api", "svc-api@example.com", "API Service", "service", ["services"]),
        ("svc-backup", "svc-backup@example.com", "Backup Service", "service", ["services", "backup"]),
        ("david.lee", "david.lee@example.com", "David Lee", "user", ["contractors"])
    ]
    
    identities = []
    for username, email, display, itype, groups in identities_data:
        identity = await zt.register_identity(username, email, display, itype, groups)
        identity.verified = random.choice([True, True, True, False])
        identity.trust_value = random.uniform(40, 90)
        identity.trust_score = TrustScore.HIGH if identity.trust_value > 70 else TrustScore.MEDIUM
        identities.append(identity)
        print(f"  👤 {display} ({', '.join(groups[:2])})")
        
    # Register Devices
    print("\n💻 Registering Devices...")
    
    devices_data = [
        (0, "John's Laptop", "workstation", "windows", "10.0.22000"),
        (0, "John's Phone", "mobile", "ios", "16.5"),
        (1, "Jane's MacBook", "workstation", "macos", "13.4"),
        (2, "Bob's Laptop", "workstation", "windows", "11.0.22621"),
        (3, "Alice's Linux", "workstation", "linux", "Ubuntu 22.04"),
        (4, "Charlie's Laptop", "workstation", "windows", "10.0.19045"),
        (5, "API Server 1", "server", "linux", "RHEL 8.7"),
        (6, "Backup Server", "server", "linux", "Ubuntu 20.04"),
        (7, "David's Laptop", "workstation", "windows", "10.0.19044")
    ]
    
    devices = []
    for owner_idx, name, dtype, platform, osver in devices_data:
        device = await zt.register_device(name, identities[owner_idx].identity_id, dtype, platform, osver)
        if device:
            devices.append(device)
            # Update compliance
            enc = random.choice([True, True, True, False])
            av = random.choice([True, True, True, False])
            fw = random.choice([True, True, True, False])
            await zt.update_device_compliance(device.device_id, enc, av, fw)
            device.is_online = random.choice([True, True, True, False])
            device.last_seen = datetime.now()
            
    print(f"  ✓ Registered {len(devices)} devices")
    
    # Create Network Segments
    print("\n🔒 Creating Network Segments...")
    
    segments_data = [
        ("Production", SegmentationType.APPLICATION, "10.0.1.0/24", TrustScore.HIGH, "strict"),
        ("Development", SegmentationType.APPLICATION, "10.0.2.0/24", TrustScore.MEDIUM, "standard"),
        ("Database", SegmentationType.DATA, "10.0.3.0/24", TrustScore.HIGH, "complete"),
        ("Management", SegmentationType.NETWORK, "10.0.4.0/24", TrustScore.HIGH, "strict"),
        ("DMZ", SegmentationType.NETWORK, "10.0.5.0/24", TrustScore.LOW, "strict"),
        ("Guest", SegmentationType.NETWORK, "10.0.6.0/24", TrustScore.UNTRUSTED, "complete"),
        ("IoT", SegmentationType.NETWORK, "10.0.7.0/24", TrustScore.UNTRUSTED, "complete"),
        ("Backup", SegmentationType.DATA, "10.0.8.0/24", TrustScore.HIGH, "complete")
    ]
    
    segments = []
    for name, stype, cidr, trust, isolation in segments_data:
        segment = await zt.create_segment(name, stype, cidr, trust, isolation)
        segments.append(segment)
        print(f"  🔒 {name} ({cidr}, {isolation})")
        
    # Register Resources
    print("\n📦 Registering Resources...")
    
    resources_data = [
        ("Production App", "application", "https://app.example.com", segments[0].segment_id, "restricted", True),
        ("API Gateway", "api", "https://api.example.com", segments[0].segment_id, "confidential", True),
        ("Dev Environment", "application", "https://dev.example.com", segments[1].segment_id, "internal", False),
        ("Staging DB", "data", "postgres://staging-db:5432", segments[1].segment_id, "confidential", False),
        ("Production DB", "data", "postgres://prod-db:5432", segments[2].segment_id, "restricted", True),
        ("Admin Console", "application", "https://admin.example.com", segments[3].segment_id, "restricted", True),
        ("Monitoring", "service", "https://monitoring.example.com", segments[3].segment_id, "internal", True),
        ("Backup Service", "service", "https://backup.example.com", segments[7].segment_id, "confidential", True)
    ]
    
    resources = []
    for name, rtype, url, seg_id, sensitivity, mfa in resources_data:
        resource = await zt.register_resource(name, rtype, url, seg_id, sensitivity, mfa)
        if resource:
            resources.append(resource)
            print(f"  📦 {name} ({sensitivity})")
            
    # Create Zero Trust Policies
    print("\n📜 Creating Zero Trust Policies...")
    
    policies_data = [
        ("Admin Access", ["admins"], [resources[5].resource_id], 80.0, True, True, PolicyAction.ALLOW, 100),
        ("Developer Access", ["developers"], [resources[2].resource_id, resources[3].resource_id], 60.0, False, True, PolicyAction.ALLOW, 90),
        ("Production Access", ["engineering"], [resources[0].resource_id, resources[1].resource_id], 75.0, True, True, PolicyAction.ALLOW, 95),
        ("Database Access", ["admins", "developers"], [resources[4].resource_id], 85.0, True, True, PolicyAction.ALLOW, 100),
        ("Monitoring Access", ["security", "admins"], [resources[6].resource_id], 70.0, True, True, PolicyAction.ALLOW, 85),
        ("Contractor Deny", ["contractors"], [], 0.0, False, False, PolicyAction.DENY, 200),
        ("Default Deny", [], [], 0.0, False, False, PolicyAction.DENY, 0)
    ]
    
    policies = []
    for name, groups, res_ids, trust, mfa, compliance, action, priority in policies_data:
        policy = await zt.create_policy(name, groups, res_ids, trust, mfa, compliance, action, priority)
        policies.append(policy)
        print(f"  📜 {name} ({action.value})")
        
    # Create Micro-segmentation Rules
    print("\n🔐 Creating Micro-segmentation Rules...")
    
    rules_data = [
        ("Dev to Staging DB", segments[1].segment_id, segments[1].segment_id, [5432], ["tcp"], PolicyAction.ALLOW),
        ("Prod to Prod DB", segments[0].segment_id, segments[2].segment_id, [5432], ["tcp"], PolicyAction.ALLOW),
        ("Management to All", segments[3].segment_id, segments[0].segment_id, [443, 22], ["tcp"], PolicyAction.ALLOW),
        ("DMZ to Prod", segments[4].segment_id, segments[0].segment_id, [443], ["tcp"], PolicyAction.ALLOW),
        ("Backup Access", segments[3].segment_id, segments[7].segment_id, [443, 22], ["tcp"], PolicyAction.ALLOW),
        ("Block Guest", segments[5].segment_id, segments[0].segment_id, [], [], PolicyAction.DENY),
        ("Block IoT to DB", segments[6].segment_id, segments[2].segment_id, [], [], PolicyAction.DENY)
    ]
    
    seg_rules = []
    for name, src, dst, ports, protos, action in rules_data:
        rule = await zt.create_segmentation_rule(name, src, dst, ports, protos, action)
        if rule:
            seg_rules.append(rule)
            print(f"  🔐 {name} ({action.value})")
            
    # Simulate Access Requests
    print("\n🔑 Processing Access Requests...")
    
    access_requests = []
    for _ in range(20):
        identity = random.choice(identities)
        device = None
        for d in devices:
            if d.owner_identity_id == identity.identity_id:
                device = d
                break
        if not device:
            device = random.choice(devices)
            
        resource = random.choice(resources)
        
        request = await zt.process_access_request(
            identity.identity_id,
            device.device_id,
            resource.resource_id,
            f"192.168.1.{random.randint(1, 255)}",
            random.choice(["US", "UK", "DE", "RU", "CN"])
        )
        access_requests.append(request)
        
    allowed = sum(1 for r in access_requests if r.decision == AccessDecision.ALLOW)
    denied = sum(1 for r in access_requests if r.decision == AccessDecision.DENY)
    mfa_required = sum(1 for r in access_requests if r.decision == AccessDecision.REQUIRE_MFA)
    
    print(f"  ✓ Processed {len(access_requests)} requests")
    print(f"    Allowed: {allowed}, Denied: {denied}, MFA Required: {mfa_required}")
    
    # Detect Threats
    print("\n⚠️ Detecting Threats...")
    
    threats_data = [
        (ThreatType.ANOMALOUS_LOGIN, identities[7].identity_id, "", "Unusual login location detected", RiskLevel.MEDIUM),
        (ThreatType.IMPOSSIBLE_TRAVEL, identities[4].identity_id, "", "Login from different continent within 1 hour", RiskLevel.HIGH),
        (ThreatType.BRUTE_FORCE, identities[0].identity_id, "", "Multiple failed login attempts", RiskLevel.MEDIUM),
        (ThreatType.MALWARE, "", devices[8].device_id, "Potential malware signature detected", RiskLevel.CRITICAL),
        (ThreatType.DATA_EXFILTRATION, identities[2].identity_id, "", "Large data transfer detected", RiskLevel.HIGH)
    ]
    
    threats = []
    for ttype, iid, did, desc, severity in threats_data:
        threat = await zt.detect_threat(ttype, iid, did, desc, severity)
        threats.append(threat)
        print(f"  ⚠️ {ttype.value}: {severity.value}")
        
    # Continuous Verification
    print("\n🔄 Running Continuous Verification...")
    
    verifications = []
    for i in range(5):
        identity = identities[i]
        device = devices[i] if i < len(devices) else devices[0]
        
        verification = await zt.continuous_verify(
            f"sess_{uuid.uuid4().hex[:8]}",
            identity.identity_id,
            device.device_id
        )
        verifications.append(verification)
        
    print(f"  ✓ Verified {len(verifications)} sessions")
    
    # Identities
    print("\n👤 Identities:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Username             │ Type    │ Groups                     │ Trust Score │ Risk Level │ Verified │ Status                   │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for identity in identities:
        username = identity.username[:20].ljust(20)
        itype = identity.identity_type[:7].ljust(7)
        groups = ", ".join(identity.groups[:2])[:26].ljust(26)
        trust = f"{identity.trust_value:.0f} ({identity.trust_score.value})".ljust(11)
        risk = identity.risk_level.value[:10].ljust(10)
        verified = "✓" if identity.verified else "✗"
        verified = verified.ljust(8)
        
        status = "✓ Active" if identity.is_active else "○ Inactive"
        status = status[:24].ljust(24)
        
        print(f"  │ {username} │ {itype} │ {groups} │ {trust} │ {risk} │ {verified} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Devices
    print("\n💻 Devices:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                  │ Type        │ Platform  │ Compliance      │ Trust Score │ Encryption │ Antivirus │ Online │ Status                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for device in devices:
        name = device.name[:21].ljust(21)
        dtype = device.device_type[:11].ljust(11)
        platform = device.platform[:9].ljust(9)
        compliance = device.compliance_status.value[:15].ljust(15)
        trust = f"{device.trust_value:.0f}".ljust(11)
        enc = "✓" if device.encryption_enabled else "✗"
        enc = enc.ljust(10)
        av = "✓" if device.antivirus_enabled else "✗"
        av = av.ljust(9)
        online = "✓" if device.is_online else "✗"
        online = online.ljust(6)
        
        status_icon = {"compliant": "✓", "non_compliant": "✗", "unknown": "?", "needs_update": "⚠"}.get(device.compliance_status.value, "?")
        status = f"{status_icon} {device.compliance_status.value}"[:37].ljust(37)
        
        print(f"  │ {name} │ {dtype} │ {platform} │ {compliance} │ {trust} │ {enc} │ {av} │ {online} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Network Segments
    print("\n🔒 Network Segments:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name              │ Type         │ CIDR              │ Trust Level │ Isolation │ Resources │ Status                        │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for segment in segments:
        name = segment.name[:17].ljust(17)
        stype = segment.segment_type.value[:12].ljust(12)
        cidr = segment.cidr[:17].ljust(17)
        trust = segment.trust_level.value[:11].ljust(11)
        isolation = segment.isolation_level[:9].ljust(9)
        resources_count = str(len(segment.resource_ids)).ljust(9)
        
        status = "✓ Active" if segment.is_active else "○ Inactive"
        status = status[:29].ljust(29)
        
        print(f"  │ {name} │ {stype} │ {cidr} │ {trust} │ {isolation} │ {resources_count} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Zero Trust Policies
    print("\n📜 Zero Trust Policies:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                   │ Groups                     │ Min Trust │ MFA │ Compliance │ Action   │ Priority │ Status              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:22].ljust(22)
        groups = ", ".join(policy.identity_groups[:2]) if policy.identity_groups else "All"
        groups = groups[:26].ljust(26)
        trust = f"{policy.min_trust_score:.0f}".ljust(9)
        mfa = "✓" if policy.require_mfa else "✗"
        mfa = mfa.ljust(3)
        compliance = "✓" if policy.require_device_compliance else "✗"
        compliance = compliance.ljust(10)
        action = policy.action.value[:8].ljust(8)
        priority = str(policy.priority).ljust(8)
        
        status = "✓ Enabled" if policy.is_enabled else "○ Disabled"
        status = status[:19].ljust(19)
        
        print(f"  │ {name} │ {groups} │ {trust} │ {mfa} │ {compliance} │ {action} │ {priority} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Access Requests
    print("\n🔑 Recent Access Requests:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ User                 │ Resource              │ Risk Score │ Decision        │ Reason                                                        │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for request in access_requests[-10:]:
        user = zt.identities.get(request.identity_id)
        username = user.username if user else "Unknown"
        username = username[:20].ljust(20)
        
        resource = zt.resources.get(request.resource_id)
        res_name = resource.name if resource else "Unknown"
        res_name = res_name[:21].ljust(21)
        
        risk = f"{request.risk_score:.0f}".ljust(10)
        
        decision_icon = {
            "allow": "✓",
            "deny": "✗",
            "require_mfa": "🔐",
            "step_up": "⬆"
        }.get(request.decision.value, "?")
        decision = f"{decision_icon} {request.decision.value}"[:15].ljust(15)
        reason = request.decision_reason[:61].ljust(61)
        
        print(f"  │ {username} │ {res_name} │ {risk} │ {decision} │ {reason} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Threats
    print("\n⚠️ Active Threats:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Threat Type              │ Severity   │ Description                                         │ Detected At          │ Status                                   │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for threat in threats:
        ttype = threat.threat_type.value[:24].ljust(24)
        severity = threat.severity.value[:10].ljust(10)
        desc = threat.description[:51].ljust(51)
        detected = threat.detected_at.strftime("%Y-%m-%d %H:%M")[:20].ljust(20)
        
        status = "🔴 Active" if threat.is_active and not threat.is_resolved else "✓ Resolved"
        status = status[:40].ljust(40)
        
        print(f"  │ {ttype} │ {severity} │ {desc} │ {detected} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Micro-segmentation Rules
    print("\n🔐 Micro-segmentation Rules:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Source           │ Destination      │ Ports           │ Action   │ Status                                            │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rule in seg_rules:
        name = rule.name[:25].ljust(25)
        
        src_seg = zt.segments.get(rule.source_segment_id)
        src = src_seg.name if src_seg else "Unknown"
        src = src[:16].ljust(16)
        
        dst_seg = zt.segments.get(rule.dest_segment_id)
        dst = dst_seg.name if dst_seg else "Unknown"
        dst = dst[:16].ljust(16)
        
        ports = ", ".join(str(p) for p in rule.allowed_ports[:3]) if rule.allowed_ports else "None"
        ports = ports[:15].ljust(15)
        
        action_icon = {"allow": "✓", "deny": "✗", "monitor": "👁", "alert": "🔔"}.get(rule.action.value, "?")
        action = f"{action_icon} {rule.action.value}"[:8].ljust(8)
        
        status = "✓ Enabled" if rule.is_enabled else "○ Disabled"
        status = status[:49].ljust(49)
        
        print(f"  │ {name} │ {src} │ {dst} │ {ports} │ {action} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = zt.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Identities: {stats['active_identities']}/{stats['total_identities']} active")
    print(f"  Verified Identities: {stats['verified_identities']}")
    print(f"  Devices: {stats['compliant_devices']}/{stats['total_devices']} compliant")
    print(f"  Network Segments: {stats['total_segments']}")
    print(f"  Resources: {stats['total_resources']}")
    print(f"  Policies: {stats['enabled_policies']}/{stats['total_policies']} enabled")
    print(f"  Access Requests: {stats['allowed_requests']} allowed, {stats['denied_requests']} denied")
    print(f"  Active Threats: {stats['active_threats']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Zero Trust Security Platform                    │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Identities:            {stats['active_identities']:>12}                      │")
    print(f"│ Compliant Devices:            {stats['compliant_devices']:>12}                      │")
    print(f"│ Network Segments:             {stats['total_segments']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Access Allowed:               {stats['allowed_requests']:>12}                      │")
    print(f"│ Access Denied:                {stats['denied_requests']:>12}                      │")
    print(f"│ Active Threats:               {stats['active_threats']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Zero Trust Security Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
