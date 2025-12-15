#!/usr/bin/env python3
"""
Server Init - Iteration 340: Privileged Access Management Platform
Платформа управления привилегированным доступом (PAM)

Функционал:
- Credential Vaulting - хранение учетных данных
- Session Management - управление сессиями
- Just-in-Time Access - доступ по требованию
- Password Rotation - ротация паролей
- Session Recording - запись сессий
- Access Request Workflow - процесс запроса доступа
- Privilege Elevation - повышение привилегий
- Audit & Compliance - аудит и соответствие
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import hashlib


class AccountType(Enum):
    """Тип привилегированного аккаунта"""
    LOCAL_ADMIN = "local_admin"
    DOMAIN_ADMIN = "domain_admin"
    SERVICE_ACCOUNT = "service_account"
    DATABASE_ADMIN = "database_admin"
    CLOUD_ADMIN = "cloud_admin"
    ROOT = "root"
    APPLICATION = "application"
    SHARED = "shared"


class SessionType(Enum):
    """Тип сессии"""
    SSH = "ssh"
    RDP = "rdp"
    DATABASE = "database"
    WEB = "web"
    API = "api"
    CONSOLE = "console"


class SessionStatus(Enum):
    """Статус сессии"""
    PENDING = "pending"
    ACTIVE = "active"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    LOCKED = "locked"


class RequestStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ElevationType(Enum):
    """Тип повышения привилегий"""
    SUDO = "sudo"
    RUN_AS = "run_as"
    IMPERSONATION = "impersonation"
    TEMPORARY_ROLE = "temporary_role"


class RotationPolicy(Enum):
    """Политика ротации"""
    AFTER_USE = "after_use"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    NEVER = "never"


class RiskLevel(Enum):
    """Уровень риска"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PrivilegedAccount:
    """Привилегированный аккаунт"""
    account_id: str
    name: str
    
    # Type
    account_type: AccountType = AccountType.LOCAL_ADMIN
    
    # Credentials
    username: str = ""
    password_hash: str = ""
    
    # Target
    target_system: str = ""
    target_host: str = ""
    target_port: int = 0
    
    # Domain/Scope
    domain: str = ""
    
    # Rotation
    rotation_policy: RotationPolicy = RotationPolicy.SCHEDULED
    rotation_interval_days: int = 30
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    
    # Access
    checkout_count: int = 0
    max_checkout_hours: int = 8
    
    # Status
    is_enabled: bool = True
    is_checked_out: bool = False
    checked_out_by: str = ""
    checked_out_at: Optional[datetime] = None
    
    # Risk
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None


@dataclass
class CredentialVault:
    """Хранилище учетных данных"""
    vault_id: str
    name: str
    
    # Account IDs
    account_ids: List[str] = field(default_factory=list)
    
    # Access
    owner_id: str = ""
    allowed_groups: List[str] = field(default_factory=list)
    
    # Encryption
    encryption_key_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessRequest:
    """Запрос на доступ"""
    request_id: str
    
    # Requester
    requester_id: str = ""
    requester_name: str = ""
    
    # Target
    account_id: str = ""
    account_name: str = ""
    
    # Request details
    reason: str = ""
    duration_hours: int = 1
    
    # Approval
    status: RequestStatus = RequestStatus.PENDING
    approver_id: str = ""
    approval_notes: str = ""
    
    # Time
    requested_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Risk
    risk_score: float = 0.0


@dataclass
class PrivilegedSession:
    """Привилегированная сессия"""
    session_id: str
    
    # User
    user_id: str = ""
    user_name: str = ""
    
    # Account
    account_id: str = ""
    account_name: str = ""
    
    # Connection
    session_type: SessionType = SessionType.SSH
    target_host: str = ""
    target_port: int = 22
    
    # Status
    status: SessionStatus = SessionStatus.PENDING
    
    # Time
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    max_duration_hours: int = 8
    
    # Recording
    is_recorded: bool = True
    recording_id: str = ""
    
    # Activity
    commands_count: int = 0
    keystrokes_count: int = 0
    
    # Risk
    risk_alerts: List[str] = field(default_factory=list)
    
    # Source
    source_ip: str = ""
    source_device: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionRecording:
    """Запись сессии"""
    recording_id: str
    
    # Session
    session_id: str = ""
    
    # Recording data
    duration_seconds: int = 0
    size_bytes: int = 0
    
    # Type
    recording_type: str = "video"  # video, text, keystroke
    
    # Storage
    storage_path: str = ""
    
    # Status
    status: str = "recording"  # recording, completed, archived
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


@dataclass
class PrivilegeElevation:
    """Повышение привилегий"""
    elevation_id: str
    
    # User
    user_id: str = ""
    
    # Type
    elevation_type: ElevationType = ElevationType.SUDO
    
    # Target
    target_command: str = ""
    target_role: str = ""
    
    # Authorization
    authorized_by: str = ""  # request_id or policy_id
    
    # Time
    started_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    
    # Audit
    commands_executed: List[str] = field(default_factory=list)


@dataclass
class PAMPolicy:
    """Политика PAM"""
    policy_id: str
    name: str
    
    # Scope
    account_types: List[AccountType] = field(default_factory=list)
    target_systems: List[str] = field(default_factory=list)
    user_groups: List[str] = field(default_factory=list)
    
    # Access rules
    require_approval: bool = True
    approvers: List[str] = field(default_factory=list)
    max_session_hours: int = 8
    
    # Checkout rules
    allow_checkout: bool = True
    max_checkout_hours: int = 4
    
    # MFA
    require_mfa: bool = True
    
    # Recording
    require_recording: bool = True
    
    # Rotation
    auto_rotate_after_use: bool = False
    
    # Time restrictions
    allowed_hours: List[int] = field(default_factory=list)  # 0-23
    allowed_days: List[int] = field(default_factory=list)  # 0-6
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PasswordRotationJob:
    """Задание на ротацию пароля"""
    job_id: str
    
    # Account
    account_id: str = ""
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    
    # Result
    old_password_hash: str = ""
    new_password_hash: str = ""
    error_message: str = ""
    
    # Timestamps
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AuditEvent:
    """Событие аудита"""
    event_id: str
    
    # Event type
    event_type: str = ""
    
    # Subject
    user_id: str = ""
    account_id: str = ""
    session_id: str = ""
    
    # Action
    action: str = ""
    target: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""
    
    # Risk
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Context
    source_ip: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class PAMManager:
    """Менеджер привилегированного доступа"""
    
    def __init__(self):
        self.accounts: Dict[str, PrivilegedAccount] = {}
        self.vaults: Dict[str, CredentialVault] = {}
        self.requests: Dict[str, AccessRequest] = {}
        self.sessions: Dict[str, PrivilegedSession] = {}
        self.recordings: Dict[str, SessionRecording] = {}
        self.elevations: Dict[str, PrivilegeElevation] = {}
        self.policies: Dict[str, PAMPolicy] = {}
        self.rotation_jobs: Dict[str, PasswordRotationJob] = {}
        self.audit_events: List[AuditEvent] = []
        
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _generate_password(self, length: int = 32) -> str:
        """Генерация пароля"""
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
        
    async def create_vault(self, name: str,
                          owner_id: str,
                          allowed_groups: List[str] = None) -> CredentialVault:
        """Создание хранилища"""
        vault = CredentialVault(
            vault_id=f"vault_{uuid.uuid4().hex[:8]}",
            name=name,
            owner_id=owner_id,
            allowed_groups=allowed_groups or [],
            encryption_key_id=f"key_{uuid.uuid4().hex[:8]}"
        )
        
        self.vaults[vault.vault_id] = vault
        
        # Audit
        await self._log_audit("create_vault", "", "", "", vault.vault_id, True)
        
        return vault
        
    async def create_account(self, name: str,
                            vault_id: str,
                            account_type: AccountType,
                            username: str,
                            password: str,
                            target_system: str,
                            target_host: str,
                            target_port: int = 22,
                            domain: str = "",
                            rotation_policy: RotationPolicy = RotationPolicy.SCHEDULED,
                            rotation_interval_days: int = 30,
                            risk_level: RiskLevel = RiskLevel.MEDIUM,
                            labels: Dict[str, str] = None) -> Optional[PrivilegedAccount]:
        """Создание привилегированного аккаунта"""
        vault = self.vaults.get(vault_id)
        if not vault:
            return None
            
        account = PrivilegedAccount(
            account_id=f"acc_{uuid.uuid4().hex[:12]}",
            name=name,
            account_type=account_type,
            username=username,
            password_hash=self._hash_password(password),
            target_system=target_system,
            target_host=target_host,
            target_port=target_port,
            domain=domain,
            rotation_policy=rotation_policy,
            rotation_interval_days=rotation_interval_days,
            risk_level=risk_level,
            labels=labels or {}
        )
        
        if rotation_policy == RotationPolicy.SCHEDULED:
            account.next_rotation = datetime.now() + timedelta(days=rotation_interval_days)
            
        vault.account_ids.append(account.account_id)
        self.accounts[account.account_id] = account
        
        # Audit
        await self._log_audit("create_account", "", account.account_id, "", account.name, True)
        
        return account
        
    async def create_policy(self, name: str,
                           account_types: List[AccountType] = None,
                           target_systems: List[str] = None,
                           user_groups: List[str] = None,
                           require_approval: bool = True,
                           approvers: List[str] = None,
                           max_session_hours: int = 8,
                           require_mfa: bool = True,
                           require_recording: bool = True,
                           auto_rotate_after_use: bool = False) -> PAMPolicy:
        """Создание политики PAM"""
        policy = PAMPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            account_types=account_types or [],
            target_systems=target_systems or [],
            user_groups=user_groups or [],
            require_approval=require_approval,
            approvers=approvers or [],
            max_session_hours=max_session_hours,
            require_mfa=require_mfa,
            require_recording=require_recording,
            auto_rotate_after_use=auto_rotate_after_use
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def request_access(self, requester_id: str,
                            requester_name: str,
                            account_id: str,
                            reason: str,
                            duration_hours: int = 1) -> Optional[AccessRequest]:
        """Запрос доступа"""
        account = self.accounts.get(account_id)
        if not account or not account.is_enabled:
            return None
            
        request = AccessRequest(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            requester_id=requester_id,
            requester_name=requester_name,
            account_id=account_id,
            account_name=account.name,
            reason=reason,
            duration_hours=duration_hours
        )
        
        # Calculate risk score
        request.risk_score = self._calculate_risk_score(account, requester_id)
        
        # Check if auto-approval is possible
        applicable_policies = self._get_applicable_policies(account)
        auto_approve = not any(p.require_approval for p in applicable_policies)
        
        if auto_approve:
            request.status = RequestStatus.APPROVED
            request.approved_at = datetime.now()
            request.expires_at = datetime.now() + timedelta(hours=duration_hours)
            request.approver_id = "system"
            
        self.requests[request.request_id] = request
        
        # Audit
        await self._log_audit("request_access", requester_id, account_id, "", reason, True)
        
        return request
        
    async def approve_request(self, request_id: str,
                             approver_id: str,
                             notes: str = "") -> bool:
        """Одобрение запроса"""
        request = self.requests.get(request_id)
        if not request or request.status != RequestStatus.PENDING:
            return False
            
        request.status = RequestStatus.APPROVED
        request.approver_id = approver_id
        request.approval_notes = notes
        request.approved_at = datetime.now()
        request.expires_at = datetime.now() + timedelta(hours=request.duration_hours)
        
        # Audit
        await self._log_audit("approve_request", approver_id, request.account_id, "", f"Approved: {notes}", True)
        
        return True
        
    async def deny_request(self, request_id: str,
                          approver_id: str,
                          reason: str = "") -> bool:
        """Отклонение запроса"""
        request = self.requests.get(request_id)
        if not request or request.status != RequestStatus.PENDING:
            return False
            
        request.status = RequestStatus.DENIED
        request.approver_id = approver_id
        request.approval_notes = reason
        
        # Audit
        await self._log_audit("deny_request", approver_id, request.account_id, "", f"Denied: {reason}", True)
        
        return True
        
    async def checkout_credential(self, account_id: str,
                                  user_id: str,
                                  request_id: str = "") -> Optional[str]:
        """Получение учетных данных"""
        account = self.accounts.get(account_id)
        if not account or not account.is_enabled:
            return None
            
        # Check if already checked out
        if account.is_checked_out:
            return None
            
        # Check request if provided
        if request_id:
            request = self.requests.get(request_id)
            if not request or request.status != RequestStatus.APPROVED:
                return None
            if request.expires_at and request.expires_at < datetime.now():
                return None
                
        # Mark as checked out
        account.is_checked_out = True
        account.checked_out_by = user_id
        account.checked_out_at = datetime.now()
        account.checkout_count += 1
        
        # Audit
        await self._log_audit("checkout_credential", user_id, account_id, "", "Credential checked out", True)
        
        # Return simulated password
        return f"PAM_CREDENTIAL_{uuid.uuid4().hex[:16]}"
        
    async def checkin_credential(self, account_id: str,
                                user_id: str) -> bool:
        """Возврат учетных данных"""
        account = self.accounts.get(account_id)
        if not account or not account.is_checked_out:
            return False
            
        account.is_checked_out = False
        account.checked_out_by = ""
        account.checked_out_at = None
        account.last_used = datetime.now()
        
        # Check if rotation is needed
        applicable_policies = self._get_applicable_policies(account)
        if any(p.auto_rotate_after_use for p in applicable_policies):
            await self.rotate_password(account_id, user_id)
            
        # Audit
        await self._log_audit("checkin_credential", user_id, account_id, "", "Credential checked in", True)
        
        return True
        
    async def start_session(self, user_id: str,
                           user_name: str,
                           account_id: str,
                           session_type: SessionType,
                           source_ip: str,
                           request_id: str = "") -> Optional[PrivilegedSession]:
        """Начало привилегированной сессии"""
        account = self.accounts.get(account_id)
        if not account or not account.is_enabled:
            return None
            
        # Get applicable policies
        applicable_policies = self._get_applicable_policies(account)
        max_hours = min(p.max_session_hours for p in applicable_policies) if applicable_policies else 8
        require_recording = any(p.require_recording for p in applicable_policies)
        
        session = PrivilegedSession(
            session_id=f"sess_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            user_name=user_name,
            account_id=account_id,
            account_name=account.name,
            session_type=session_type,
            target_host=account.target_host,
            target_port=account.target_port,
            status=SessionStatus.ACTIVE,
            started_at=datetime.now(),
            max_duration_hours=max_hours,
            is_recorded=require_recording,
            source_ip=source_ip
        )
        
        # Create recording if required
        if require_recording:
            recording = SessionRecording(
                recording_id=f"rec_{uuid.uuid4().hex[:12]}",
                session_id=session.session_id,
                storage_path=f"/recordings/{session.session_id}/"
            )
            session.recording_id = recording.recording_id
            self.recordings[recording.recording_id] = recording
            
        self.sessions[session.session_id] = session
        
        # Audit
        await self._log_audit("start_session", user_id, account_id, session.session_id, 
                            f"Session started: {session_type.value}", True)
        
        return session
        
    async def end_session(self, session_id: str,
                         user_id: str) -> bool:
        """Завершение сессии"""
        session = self.sessions.get(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            return False
            
        session.status = SessionStatus.TERMINATED
        session.ended_at = datetime.now()
        
        # End recording
        if session.recording_id:
            recording = self.recordings.get(session.recording_id)
            if recording:
                recording.status = "completed"
                recording.ended_at = datetime.now()
                if session.ended_at and session.started_at:
                    recording.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
                recording.size_bytes = random.randint(1000000, 50000000)  # Simulated
                
        # Update account
        account = self.accounts.get(session.account_id)
        if account:
            account.last_used = datetime.now()
            
        # Audit
        await self._log_audit("end_session", user_id, session.account_id, session_id, 
                            "Session ended", True)
        
        return True
        
    async def terminate_session(self, session_id: str,
                               admin_id: str,
                               reason: str = "") -> bool:
        """Принудительное завершение сессии"""
        session = self.sessions.get(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            return False
            
        session.status = SessionStatus.TERMINATED
        session.ended_at = datetime.now()
        session.risk_alerts.append(f"Terminated by admin: {reason}")
        
        # Audit
        await self._log_audit("terminate_session", admin_id, session.account_id, session_id, 
                            f"Session terminated: {reason}", True, risk_level=RiskLevel.HIGH)
        
        return True
        
    async def elevate_privileges(self, user_id: str,
                                elevation_type: ElevationType,
                                target_command: str = "",
                                target_role: str = "",
                                duration_hours: int = 1) -> Optional[PrivilegeElevation]:
        """Повышение привилегий"""
        elevation = PrivilegeElevation(
            elevation_id=f"elev_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            elevation_type=elevation_type,
            target_command=target_command,
            target_role=target_role,
            authorized_by="policy",
            expires_at=datetime.now() + timedelta(hours=duration_hours)
        )
        
        self.elevations[elevation.elevation_id] = elevation
        
        # Audit
        await self._log_audit("elevate_privileges", user_id, "", "", 
                            f"Privilege elevation: {elevation_type.value}", True, 
                            risk_level=RiskLevel.HIGH)
        
        return elevation
        
    async def rotate_password(self, account_id: str,
                             principal_id: str) -> Optional[PasswordRotationJob]:
        """Ротация пароля"""
        account = self.accounts.get(account_id)
        if not account:
            return None
            
        job = PasswordRotationJob(
            job_id=f"rot_{uuid.uuid4().hex[:8]}",
            account_id=account_id,
            old_password_hash=account.password_hash,
            status="in_progress",
            started_at=datetime.now()
        )
        
        # Generate new password
        new_password = self._generate_password()
        account.password_hash = self._hash_password(new_password)
        account.last_rotated = datetime.now()
        
        if account.rotation_policy == RotationPolicy.SCHEDULED:
            account.next_rotation = datetime.now() + timedelta(days=account.rotation_interval_days)
            
        job.new_password_hash = account.password_hash
        job.status = "completed"
        job.completed_at = datetime.now()
        
        self.rotation_jobs[job.job_id] = job
        
        # Audit
        await self._log_audit("rotate_password", principal_id, account_id, "", 
                            "Password rotated", True)
        
        return job
        
    def _calculate_risk_score(self, account: PrivilegedAccount, user_id: str) -> float:
        """Расчет уровня риска"""
        score = 0.0
        
        # Account type risk
        type_scores = {
            AccountType.ROOT: 40.0,
            AccountType.DOMAIN_ADMIN: 35.0,
            AccountType.CLOUD_ADMIN: 30.0,
            AccountType.DATABASE_ADMIN: 25.0,
            AccountType.LOCAL_ADMIN: 20.0,
            AccountType.SERVICE_ACCOUNT: 15.0,
            AccountType.APPLICATION: 10.0,
            AccountType.SHARED: 25.0
        }
        score += type_scores.get(account.account_type, 10.0)
        
        # Account risk level
        risk_scores = {
            RiskLevel.CRITICAL: 30.0,
            RiskLevel.HIGH: 20.0,
            RiskLevel.MEDIUM: 10.0,
            RiskLevel.LOW: 5.0
        }
        score += risk_scores.get(account.risk_level, 10.0)
        
        # Other factors
        if account.is_checked_out:
            score += 10.0
            
        return min(100.0, score)
        
    def _get_applicable_policies(self, account: PrivilegedAccount) -> List[PAMPolicy]:
        """Получение применимых политик"""
        result = []
        
        for policy in self.policies.values():
            if not policy.is_enabled:
                continue
                
            # Check account type
            if policy.account_types and account.account_type not in policy.account_types:
                continue
                
            # Check target system
            if policy.target_systems and account.target_system not in policy.target_systems:
                continue
                
            result.append(policy)
            
        return result
        
    async def _log_audit(self, event_type: str,
                        user_id: str,
                        account_id: str,
                        session_id: str,
                        action: str,
                        success: bool,
                        risk_level: RiskLevel = RiskLevel.LOW):
        """Запись в аудит"""
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            user_id=user_id,
            account_id=account_id,
            session_id=session_id,
            action=action,
            success=success,
            risk_level=risk_level
        )
        
        self.audit_events.append(event)
        
    def get_accounts_needing_rotation(self) -> List[PrivilegedAccount]:
        """Получение аккаунтов, требующих ротации"""
        result = []
        now = datetime.now()
        
        for account in self.accounts.values():
            if not account.is_enabled:
                continue
            if account.rotation_policy != RotationPolicy.SCHEDULED:
                continue
            if account.next_rotation and account.next_rotation <= now:
                result.append(account)
                
        return result
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_accounts = len(self.accounts)
        enabled_accounts = sum(1 for a in self.accounts.values() if a.is_enabled)
        checked_out = sum(1 for a in self.accounts.values() if a.is_checked_out)
        
        # By type
        by_type = {}
        for account in self.accounts.values():
            t = account.account_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        total_vaults = len(self.vaults)
        
        total_requests = len(self.requests)
        pending_requests = sum(1 for r in self.requests.values() if r.status == RequestStatus.PENDING)
        approved_requests = sum(1 for r in self.requests.values() if r.status == RequestStatus.APPROVED)
        
        total_sessions = len(self.sessions)
        active_sessions = sum(1 for s in self.sessions.values() if s.status == SessionStatus.ACTIVE)
        
        total_recordings = len(self.recordings)
        
        total_policies = len(self.policies)
        
        needing_rotation = len(self.get_accounts_needing_rotation())
        
        return {
            "total_accounts": total_accounts,
            "enabled_accounts": enabled_accounts,
            "checked_out_accounts": checked_out,
            "accounts_by_type": by_type,
            "total_vaults": total_vaults,
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_recordings": total_recordings,
            "total_policies": total_policies,
            "accounts_needing_rotation": needing_rotation
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 340: Privileged Access Management")
    print("=" * 60)
    
    pam = PAMManager()
    print("✓ PAM Manager initialized")
    
    # Create Vaults
    print("\n🏦 Creating Credential Vaults...")
    
    vaults_data = [
        ("Production Servers", "admin", ["sre-team", "admins"]),
        ("Database Credentials", "dba-team", ["dba-team", "admins"]),
        ("Cloud Accounts", "cloud-team", ["cloud-team", "admins"]),
        ("Service Accounts", "security-team", ["security-team", "sre-team"]),
        ("Development", "dev-lead", ["developers", "qa-team"])
    ]
    
    vaults = []
    for name, owner, groups in vaults_data:
        vault = await pam.create_vault(name, owner, groups)
        vaults.append(vault)
        print(f"  🏦 {name}")
        
    # Create PAM Policies
    print("\n📜 Creating PAM Policies...")
    
    policies_data = [
        ("Critical Systems", [AccountType.ROOT, AccountType.DOMAIN_ADMIN], ["production"], True, ["security-lead", "cto"], 4, True, True, True),
        ("Database Access", [AccountType.DATABASE_ADMIN], ["database"], True, ["dba-lead"], 8, True, True, False),
        ("Cloud Admin", [AccountType.CLOUD_ADMIN], ["aws", "azure", "gcp"], True, ["cloud-lead"], 4, True, True, True),
        ("Service Accounts", [AccountType.SERVICE_ACCOUNT], [], False, [], 24, False, True, False),
        ("Development", [AccountType.LOCAL_ADMIN], ["development"], False, [], 8, False, False, False)
    ]
    
    policies = []
    for name, types, systems, approve, approvers, max_hours, mfa, record, rotate in policies_data:
        policy = await pam.create_policy(
            name, types, systems, [],
            approve, approvers, max_hours, mfa, record, rotate
        )
        policies.append(policy)
        print(f"  📜 {name}")
        
    # Create Privileged Accounts
    print("\n🔑 Creating Privileged Accounts...")
    
    accounts_data = [
        (vaults[0].vault_id, "Linux Root - Prod Web", AccountType.ROOT, "root", "prod-web-01.example.com", 22, "", "production", RiskLevel.CRITICAL),
        (vaults[0].vault_id, "Linux Root - Prod DB", AccountType.ROOT, "root", "prod-db-01.example.com", 22, "", "production", RiskLevel.CRITICAL),
        (vaults[0].vault_id, "Windows Admin - DC", AccountType.DOMAIN_ADMIN, "Administrator", "dc01.example.com", 3389, "example.com", "production", RiskLevel.CRITICAL),
        (vaults[1].vault_id, "PostgreSQL Admin", AccountType.DATABASE_ADMIN, "postgres", "prod-postgres.example.com", 5432, "", "database", RiskLevel.HIGH),
        (vaults[1].vault_id, "MySQL Admin", AccountType.DATABASE_ADMIN, "root", "prod-mysql.example.com", 3306, "", "database", RiskLevel.HIGH),
        (vaults[2].vault_id, "AWS Root Account", AccountType.CLOUD_ADMIN, "aws-root", "aws.amazon.com", 443, "", "aws", RiskLevel.CRITICAL),
        (vaults[2].vault_id, "Azure Admin", AccountType.CLOUD_ADMIN, "azure-admin@example.com", "portal.azure.com", 443, "", "azure", RiskLevel.HIGH),
        (vaults[3].vault_id, "Jenkins Service", AccountType.SERVICE_ACCOUNT, "jenkins-svc", "jenkins.example.com", 22, "", "ci-cd", RiskLevel.MEDIUM),
        (vaults[3].vault_id, "Backup Service", AccountType.SERVICE_ACCOUNT, "backup-svc", "backup.example.com", 22, "", "backup", RiskLevel.MEDIUM),
        (vaults[4].vault_id, "Dev Admin", AccountType.LOCAL_ADMIN, "dev-admin", "dev-server.example.com", 22, "", "development", RiskLevel.LOW)
    ]
    
    accounts = []
    for vault_id, name, atype, username, host, port, domain, system, risk in accounts_data:
        account = await pam.create_account(
            name, vault_id, atype, username,
            f"password_{uuid.uuid4().hex[:8]}",
            system, host, port, domain,
            RotationPolicy.SCHEDULED, 30, risk
        )
        if account:
            accounts.append(account)
            print(f"  🔑 {name} ({atype.value})")
            
    # Simulate Access Requests
    print("\n📝 Processing Access Requests...")
    
    requests_data = [
        ("user-001", "John Doe", accounts[0].account_id, "Emergency maintenance", 2),
        ("user-002", "Jane Smith", accounts[3].account_id, "Database migration", 4),
        ("user-003", "Bob Wilson", accounts[6].account_id, "Cloud infrastructure update", 2),
        ("user-004", "Alice Johnson", accounts[9].account_id, "Development testing", 8),
        ("user-005", "Charlie Brown", accounts[1].account_id, "System patching", 4)
    ]
    
    requests = []
    for user_id, user_name, account_id, reason, hours in requests_data:
        request = await pam.request_access(user_id, user_name, account_id, reason, hours)
        if request:
            requests.append(request)
            print(f"  📝 {user_name} → {pam.accounts[account_id].name}")
            
    # Approve/Deny requests
    print("\n✅ Processing Approvals...")
    
    approved = 0
    denied = 0
    for i, request in enumerate(requests):
        if request.status == RequestStatus.PENDING:
            if i % 3 == 0:  # Deny every 3rd
                await pam.deny_request(request.request_id, "security-lead", "Not authorized for this time")
                denied += 1
            else:
                await pam.approve_request(request.request_id, "security-lead", "Approved for maintenance window")
                approved += 1
                
    print(f"  ✅ Approved: {approved}, Denied: {denied}")
    
    # Checkout credentials and start sessions
    print("\n🎫 Starting Privileged Sessions...")
    
    sessions = []
    for request in requests:
        if request.status == RequestStatus.APPROVED:
            # Checkout credential
            cred = await pam.checkout_credential(request.account_id, request.requester_id, request.request_id)
            
            if cred:
                # Start session
                account = pam.accounts[request.account_id]
                session_type = SessionType.SSH if account.target_port == 22 else (
                    SessionType.RDP if account.target_port == 3389 else SessionType.DATABASE
                )
                
                session = await pam.start_session(
                    request.requester_id,
                    request.requester_name,
                    request.account_id,
                    session_type,
                    f"192.168.1.{random.randint(1, 255)}",
                    request.request_id
                )
                
                if session:
                    sessions.append(session)
                    session.commands_count = random.randint(5, 50)
                    session.keystrokes_count = random.randint(100, 2000)
                    print(f"  🎫 {request.requester_name} → {account.name} ({session_type.value})")
                    
    # Privilege elevations
    print("\n⬆️ Processing Privilege Elevations...")
    
    elevations_data = [
        ("user-001", ElevationType.SUDO, "apt-get update && apt-get upgrade", ""),
        ("user-002", ElevationType.RUN_AS, "", "db_admin"),
        ("user-003", ElevationType.TEMPORARY_ROLE, "", "CloudAdmin")
    ]
    
    elevations = []
    for user_id, etype, cmd, role in elevations_data:
        elevation = await pam.elevate_privileges(user_id, etype, cmd, role, 1)
        if elevation:
            elevations.append(elevation)
            print(f"  ⬆️ {user_id}: {etype.value}")
            
    # End some sessions
    print("\n🔚 Ending Sessions...")
    
    ended = 0
    for session in sessions[:2]:
        await pam.end_session(session.session_id, session.user_id)
        await pam.checkin_credential(session.account_id, session.user_id)
        ended += 1
        
    print(f"  🔚 Ended {ended} sessions")
    
    # Rotate passwords
    print("\n🔄 Rotating Passwords...")
    
    rotated = 0
    for account in accounts[:3]:
        job = await pam.rotate_password(account.account_id, "admin")
        if job and job.status == "completed":
            rotated += 1
            
    print(f"  🔄 Rotated {rotated} passwords")
    
    # Credential Vaults
    print("\n🏦 Credential Vaults:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                        │ Owner          │ Accounts │ Allowed Groups                          │ Status                                  │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for vault in vaults:
        name = vault.name[:27].ljust(27)
        owner = vault.owner_id[:14].ljust(14)
        acc_count = str(len(vault.account_ids)).ljust(8)
        groups = ", ".join(vault.allowed_groups[:3])[:39].ljust(39)
        status = "✓ Active" if vault.is_active else "○ Inactive"
        status = status[:41].ljust(41)
        
        print(f"  │ {name} │ {owner} │ {acc_count} │ {groups} │ {status} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Privileged Accounts
    print("\n🔑 Privileged Accounts:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Type              │ Username      │ Target Host              │ Risk     │ Checked Out │ Last Rotated         │ Status                                                                 │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for account in accounts:
        name = account.name[:28].ljust(28)
        atype = account.account_type.value[:17].ljust(17)
        username = account.username[:13].ljust(13)
        host = account.target_host[:24].ljust(24)
        
        risk_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(account.risk_level.value, "⚪")
        risk = f"{risk_icon} {account.risk_level.value}"[:8].ljust(8)
        
        checkout = "Yes" if account.is_checked_out else "No"
        checkout = checkout[:11].ljust(11)
        
        rotated = account.last_rotated.strftime("%Y-%m-%d %H:%M") if account.last_rotated else "Never"
        rotated = rotated[:20].ljust(20)
        
        status = "✓ Enabled" if account.is_enabled else "○ Disabled"
        status = status[:72].ljust(72)
        
        print(f"  │ {name} │ {atype} │ {username} │ {host} │ {risk} │ {checkout} │ {rotated} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Access Requests
    print("\n📝 Access Requests:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Requester            │ Account                      │ Reason                                  │ Duration │ Risk Score │ Status                                                                                     │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for request in requests:
        requester = request.requester_name[:20].ljust(20)
        account = request.account_name[:28].ljust(28)
        reason = request.reason[:39].ljust(39)
        duration = f"{request.duration_hours}h".ljust(8)
        risk = f"{request.risk_score:.0f}".ljust(10)
        
        status_icon = {"pending": "⏳", "approved": "✓", "denied": "✗", "expired": "⏰"}.get(request.status.value, "?")
        status = f"{status_icon} {request.status.value}"[:92].ljust(92)
        
        print(f"  │ {requester} │ {account} │ {reason} │ {duration} │ {risk} │ {status} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Active Sessions
    print("\n🎫 Privileged Sessions:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ User                 │ Account                      │ Type       │ Target Host              │ Commands │ Recorded │ Status                                                          │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for session in sessions:
        user = session.user_name[:20].ljust(20)
        account = session.account_name[:28].ljust(28)
        stype = session.session_type.value[:10].ljust(10)
        host = session.target_host[:24].ljust(24)
        cmds = str(session.commands_count).ljust(8)
        recorded = "✓" if session.is_recorded else "✗"
        recorded = recorded.ljust(8)
        
        status_icon = {"active": "🟢", "terminated": "⚫", "pending": "🟡"}.get(session.status.value, "⚪")
        status = f"{status_icon} {session.status.value}"[:65].ljust(65)
        
        print(f"  │ {user} │ {account} │ {stype} │ {host} │ {cmds} │ {recorded} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # PAM Policies
    print("\n📜 PAM Policies:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                      │ Account Types               │ Max Hours │ Approval │ MFA │ Recording │ Auto-Rotate │ Status                                              │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for policy in policies:
        name = policy.name[:25].ljust(25)
        types = ", ".join(t.value[:8] for t in policy.account_types[:2]) if policy.account_types else "All"
        types = types[:27].ljust(27)
        max_hours = f"{policy.max_session_hours}h".ljust(9)
        approval = "✓" if policy.require_approval else "✗"
        approval = approval.ljust(8)
        mfa = "✓" if policy.require_mfa else "✗"
        mfa = mfa.ljust(3)
        recording = "✓" if policy.require_recording else "✗"
        recording = recording.ljust(9)
        rotate = "✓" if policy.auto_rotate_after_use else "✗"
        rotate = rotate.ljust(11)
        status = "✓ Enabled" if policy.is_enabled else "○ Disabled"
        status = status[:53].ljust(53)
        
        print(f"  │ {name} │ {types} │ {max_hours} │ {approval} │ {mfa} │ {recording} │ {rotate} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Recent Audit Events
    print("\n📋 Recent Audit Events:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Event Type             │ User             │ Account                      │ Action                                         │ Risk     │ Timestamp            │ Status                                                    │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for event in pam.audit_events[-12:]:
        etype = event.event_type[:22].ljust(22)
        user = event.user_id[:16].ljust(16)
        
        account = pam.accounts.get(event.account_id)
        acc_name = account.name if account else event.account_id
        acc_name = acc_name[:28].ljust(28)
        
        action = event.action[:46].ljust(46)
        
        risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(event.risk_level.value, "⚪")
        risk = f"{risk_icon}".ljust(8)
        
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        
        status_icon = "✓" if event.success else "✗"
        status = f"{status_icon} {'Success' if event.success else event.error_message}"[:59].ljust(59)
        
        print(f"  │ {etype} │ {user} │ {acc_name} │ {action} │ {risk} │ {timestamp} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = pam.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Credential Vaults: {stats['total_vaults']}")
    print(f"  Privileged Accounts: {stats['enabled_accounts']}/{stats['total_accounts']} enabled")
    print(f"  Checked Out: {stats['checked_out_accounts']}")
    print(f"  Access Requests: {stats['pending_requests']} pending, {stats['approved_requests']} approved")
    print(f"  Active Sessions: {stats['active_sessions']}/{stats['total_sessions']}")
    print(f"  Session Recordings: {stats['total_recordings']}")
    print(f"  PAM Policies: {stats['total_policies']}")
    print(f"  Needing Rotation: {stats['accounts_needing_rotation']}")
    
    print("\n  Accounts by Type:")
    for atype, count in stats['accounts_by_type'].items():
        print(f"    {atype}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                Privileged Access Management Platform               │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Privileged Accounts:          {stats['total_accounts']:>12}                      │")
    print(f"│ Checked Out:                  {stats['checked_out_accounts']:>12}                      │")
    print(f"│ Credential Vaults:            {stats['total_vaults']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Pending Requests:             {stats['pending_requests']:>12}                      │")
    print(f"│ Active Sessions:              {stats['active_sessions']:>12}                      │")
    print(f"│ Session Recordings:           {stats['total_recordings']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Privileged Access Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
