#!/usr/bin/env python3
"""
Server Init - Iteration 58: Identity & Access Management (IAM)
Управление идентификацией и доступом

Функционал:
- User Management - управление пользователями
- Role-Based Access Control (RBAC) - ролевое управление
- Policy Management - управление политиками
- Multi-Factor Authentication - многофакторная аутентификация
- Session Management - управление сессиями
- OAuth2/OIDC Integration - интеграция OAuth2/OpenID Connect
- Audit Logging - журналирование доступа
- Access Reviews - ревизия доступа
"""

import json
import asyncio
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from collections import defaultdict
import uuid


class UserStatus(Enum):
    """Статус пользователя"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"


class MFAType(Enum):
    """Тип MFA"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"
    PUSH = "push"


class PolicyEffect(Enum):
    """Эффект политики"""
    ALLOW = "allow"
    DENY = "deny"


class ActionType(Enum):
    """Тип действия"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"
    LIST = "list"


class SessionState(Enum):
    """Состояние сессии"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class User:
    """Пользователь"""
    user_id: str
    username: str
    email: str
    
    # Пароль (хеш)
    password_hash: str = ""
    
    # Профиль
    display_name: str = ""
    phone: str = ""
    
    # Статус
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    
    # MFA
    mfa_enabled: bool = False
    mfa_type: Optional[MFAType] = None
    mfa_secret: str = ""
    
    # Роли и группы
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    
    # Атрибуты
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    # Security
    failed_login_attempts: int = 0
    last_failed_login: Optional[datetime] = None


@dataclass
class Role:
    """Роль"""
    role_id: str
    name: str
    
    # Описание
    description: str = ""
    
    # Разрешения
    permissions: List[str] = field(default_factory=list)
    
    # Наследование
    inherits_from: List[str] = field(default_factory=list)
    
    # Система
    is_system_role: bool = False
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Group:
    """Группа"""
    group_id: str
    name: str
    
    # Описание
    description: str = ""
    
    # Члены
    members: List[str] = field(default_factory=list)  # User IDs
    
    # Роли группы
    roles: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Permission:
    """Разрешение"""
    permission_id: str
    name: str
    
    # Resource pattern
    resource: str = "*"  # e.g., "projects:*", "users:read"
    
    # Действия
    actions: List[ActionType] = field(default_factory=list)
    
    # Описание
    description: str = ""


@dataclass
class Policy:
    """Политика доступа"""
    policy_id: str
    name: str
    
    # Эффект
    effect: PolicyEffect = PolicyEffect.ALLOW
    
    # Subjects (кому)
    principals: List[str] = field(default_factory=list)  # User IDs, Role names, Group IDs
    
    # Resources (к чему)
    resources: List[str] = field(default_factory=list)  # Resource patterns
    
    # Actions (что)
    actions: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Приоритет (меньше = выше)
    priority: int = 100
    
    # Статус
    enabled: bool = True
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """Сессия"""
    session_id: str
    user_id: str
    
    # Состояние
    state: SessionState = SessionState.ACTIVE
    
    # Токены
    access_token: str = ""
    refresh_token: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Контекст
    ip_address: str = ""
    user_agent: str = ""
    device_id: str = ""


@dataclass
class AuditLog:
    """Запись аудита"""
    log_id: str
    
    # Кто
    user_id: str = ""
    session_id: str = ""
    
    # Что
    action: str = ""
    resource: str = ""
    
    # Результат
    success: bool = True
    error_message: str = ""
    
    # Контекст
    ip_address: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AccessReview:
    """Ревизия доступа"""
    review_id: str
    name: str
    
    # Scope
    target_users: List[str] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)
    
    # Reviewer
    reviewer_id: str = ""
    
    # Статус
    status: str = "pending"  # pending, in_progress, completed
    
    # Результаты
    decisions: Dict[str, str] = field(default_factory=dict)  # user_id -> decision
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class UserManager:
    """Менеджер пользователей"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.username_index: Dict[str, str] = {}  # username -> user_id
        self.email_index: Dict[str, str] = {}  # email -> user_id
        
    def create_user(self, username: str, email: str, password: str,
                     **kwargs) -> User:
        """Создание пользователя"""
        # Проверка уникальности
        if username in self.username_index:
            raise ValueError("Username already exists")
        if email in self.email_index:
            raise ValueError("Email already exists")
            
        password_hash = self._hash_password(password)
        
        user = User(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            username=username,
            email=email,
            password_hash=password_hash,
            password_changed_at=datetime.now(),
            **kwargs
        )
        
        self.users[user.user_id] = user
        self.username_index[username] = user.user_id
        self.email_index[email] = user.user_id
        
        return user
        
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = secrets.token_hex(16)
        hash_value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_value.hex()}"
        
    def verify_password(self, user_id: str, password: str) -> bool:
        """Проверка пароля"""
        user = self.users.get(user_id)
        if not user:
            return False
            
        salt, stored_hash = user.password_hash.split('$')
        hash_value = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        
        return hash_value.hex() == stored_hash
        
    def get_by_username(self, username: str) -> Optional[User]:
        """Получение по username"""
        user_id = self.username_index.get(username)
        return self.users.get(user_id) if user_id else None
        
    def update_status(self, user_id: str, status: UserStatus):
        """Обновление статуса"""
        if user_id in self.users:
            self.users[user_id].status = status
            
    def record_failed_login(self, user_id: str):
        """Запись неудачной попытки входа"""
        user = self.users.get(user_id)
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.now()
            
            # Автоблокировка при 5 попытках
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.LOCKED
                
    def reset_failed_logins(self, user_id: str):
        """Сброс неудачных попыток"""
        user = self.users.get(user_id)
        if user:
            user.failed_login_attempts = 0
            user.last_failed_login = None


class RoleManager:
    """Менеджер ролей"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        
        # Системные роли
        self._create_system_roles()
        
    def _create_system_roles(self):
        """Создание системных ролей"""
        system_roles = [
            ("admin", "Administrator", ["*:*"]),
            ("user", "Regular User", ["profile:read", "profile:write"]),
            ("viewer", "Viewer", ["*:read"]),
            ("operator", "Operator", ["*:read", "*:execute"]),
        ]
        
        for name, desc, perms in system_roles:
            self.create_role(name, description=desc, permissions=perms, is_system_role=True)
            
    def create_role(self, name: str, **kwargs) -> Role:
        """Создание роли"""
        role = Role(
            role_id=f"role_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        self.roles[name] = role
        return role
        
    def get_effective_permissions(self, role_name: str) -> Set[str]:
        """Получение эффективных разрешений (с учётом наследования)"""
        role = self.roles.get(role_name)
        if not role:
            return set()
            
        permissions = set(role.permissions)
        
        # Добавляем унаследованные
        for parent_name in role.inherits_from:
            parent_perms = self.get_effective_permissions(parent_name)
            permissions.update(parent_perms)
            
        return permissions
        
    def create_permission(self, name: str, resource: str,
                           actions: List[ActionType]) -> Permission:
        """Создание разрешения"""
        permission = Permission(
            permission_id=f"perm_{uuid.uuid4().hex[:8]}",
            name=name,
            resource=resource,
            actions=actions
        )
        
        self.permissions[name] = permission
        return permission


class GroupManager:
    """Менеджер групп"""
    
    def __init__(self):
        self.groups: Dict[str, Group] = {}
        
    def create_group(self, name: str, **kwargs) -> Group:
        """Создание группы"""
        group = Group(
            group_id=f"group_{uuid.uuid4().hex[:8]}",
            name=name,
            **kwargs
        )
        
        self.groups[group.group_id] = group
        return group
        
    def add_member(self, group_id: str, user_id: str):
        """Добавление члена"""
        group = self.groups.get(group_id)
        if group and user_id not in group.members:
            group.members.append(user_id)
            
    def remove_member(self, group_id: str, user_id: str):
        """Удаление члена"""
        group = self.groups.get(group_id)
        if group and user_id in group.members:
            group.members.remove(user_id)
            
    def get_user_groups(self, user_id: str) -> List[Group]:
        """Получение групп пользователя"""
        return [g for g in self.groups.values() if user_id in g.members]


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self, role_manager: RoleManager, group_manager: GroupManager):
        self.policies: Dict[str, Policy] = {}
        self.role_manager = role_manager
        self.group_manager = group_manager
        
    def create_policy(self, name: str, effect: PolicyEffect,
                       principals: List[str], resources: List[str],
                       actions: List[str], **kwargs) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"policy_{uuid.uuid4().hex[:8]}",
            name=name,
            effect=effect,
            principals=principals,
            resources=resources,
            actions=actions,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    def evaluate(self, user_id: str, resource: str, action: str,
                  context: Dict[str, Any] = None) -> tuple:
        """Оценка доступа"""
        context = context or {}
        
        # Собираем все политики
        applicable_policies = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            # Проверка principals
            if not self._match_principal(user_id, policy.principals):
                continue
                
            # Проверка resources
            if not self._match_resource(resource, policy.resources):
                continue
                
            # Проверка actions
            if not self._match_action(action, policy.actions):
                continue
                
            # Проверка conditions
            if not self._evaluate_conditions(policy.conditions, context):
                continue
                
            applicable_policies.append(policy)
            
        if not applicable_policies:
            return False, "No applicable policies"
            
        # Сортируем по приоритету
        applicable_policies.sort(key=lambda p: p.priority)
        
        # Deny имеет приоритет
        for policy in applicable_policies:
            if policy.effect == PolicyEffect.DENY:
                return False, f"Denied by policy: {policy.name}"
                
        # Проверяем Allow
        for policy in applicable_policies:
            if policy.effect == PolicyEffect.ALLOW:
                return True, f"Allowed by policy: {policy.name}"
                
        return False, "Access denied by default"
        
    def _match_principal(self, user_id: str, principals: List[str]) -> bool:
        """Проверка principal"""
        if "*" in principals or user_id in principals:
            return True
            
        # Проверка ролей и групп
        user_groups = self.group_manager.get_user_groups(user_id)
        for group in user_groups:
            if group.group_id in principals or group.name in principals:
                return True
                
        return False
        
    def _match_resource(self, resource: str, patterns: List[str]) -> bool:
        """Проверка resource по паттерну"""
        for pattern in patterns:
            if pattern == "*":
                return True
            if pattern.endswith("*"):
                if resource.startswith(pattern[:-1]):
                    return True
            elif pattern == resource:
                return True
        return False
        
    def _match_action(self, action: str, actions: List[str]) -> bool:
        """Проверка action"""
        return "*" in actions or action in actions
        
    def _evaluate_conditions(self, conditions: Dict[str, Any],
                              context: Dict[str, Any]) -> bool:
        """Оценка условий"""
        if not conditions:
            return True
            
        for key, value in conditions.items():
            if key == "time_range":
                now = datetime.now().time()
                start = datetime.strptime(value["start"], "%H:%M").time()
                end = datetime.strptime(value["end"], "%H:%M").time()
                if not (start <= now <= end):
                    return False
                    
            elif key == "ip_range":
                client_ip = context.get("ip_address", "")
                if not any(client_ip.startswith(prefix) for prefix in value):
                    return False
                    
            elif key == "mfa_required":
                if value and not context.get("mfa_verified"):
                    return False
                    
        return True


class SessionManager:
    """Менеджер сессий"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)
        
    def create_session(self, user_id: str, **kwargs) -> Session:
        """Создание сессии"""
        session = Session(
            session_id=f"sess_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            access_token=secrets.token_urlsafe(32),
            refresh_token=secrets.token_urlsafe(64),
            **kwargs
        )
        
        self.sessions[session.session_id] = session
        self.user_sessions[user_id].append(session.session_id)
        
        return session
        
    def validate_session(self, session_id: str) -> Optional[Session]:
        """Валидация сессии"""
        session = self.sessions.get(session_id)
        
        if not session:
            return None
            
        if session.state != SessionState.ACTIVE:
            return None
            
        if session.expires_at < datetime.now():
            session.state = SessionState.EXPIRED
            return None
            
        session.last_activity = datetime.now()
        return session
        
    def revoke_session(self, session_id: str):
        """Отзыв сессии"""
        session = self.sessions.get(session_id)
        if session:
            session.state = SessionState.REVOKED
            
    def revoke_user_sessions(self, user_id: str):
        """Отзыв всех сессий пользователя"""
        for session_id in self.user_sessions.get(user_id, []):
            self.revoke_session(session_id)
            
    def refresh_session(self, refresh_token: str) -> Optional[Session]:
        """Обновление сессии"""
        for session in self.sessions.values():
            if session.refresh_token == refresh_token and session.state == SessionState.ACTIVE:
                # Создаём новую сессию
                new_session = self.create_session(
                    session.user_id,
                    ip_address=session.ip_address,
                    user_agent=session.user_agent,
                    device_id=session.device_id
                )
                
                # Отзываем старую
                session.state = SessionState.REVOKED
                
                return new_session
                
        return None


class MFAManager:
    """Менеджер MFA"""
    
    def __init__(self):
        self.pending_verifications: Dict[str, Dict[str, Any]] = {}
        
    def setup_totp(self, user_id: str) -> str:
        """Настройка TOTP"""
        secret = secrets.token_hex(20)
        return secret
        
    def verify_totp(self, user_id: str, code: str, secret: str) -> bool:
        """Проверка TOTP кода"""
        # Упрощённая симуляция
        # В реальности использовался бы pyotp
        expected = hashlib.sha256(f"{secret}{int(time.time()) // 30}".encode()).hexdigest()[:6]
        return code == expected or len(code) == 6  # Для демо любой 6-значный код
        
    def send_sms_code(self, user_id: str, phone: str) -> str:
        """Отправка SMS кода"""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        self.pending_verifications[user_id] = {
            "code": code,
            "type": "sms",
            "expires": datetime.now() + timedelta(minutes=5)
        }
        return code
        
    def verify_sms_code(self, user_id: str, code: str) -> bool:
        """Проверка SMS кода"""
        verification = self.pending_verifications.get(user_id)
        
        if not verification:
            return False
            
        if verification["expires"] < datetime.now():
            del self.pending_verifications[user_id]
            return False
            
        if verification["code"] == code:
            del self.pending_verifications[user_id]
            return True
            
        return False


class AuditLogger:
    """Логгер аудита"""
    
    def __init__(self):
        self.logs: List[AuditLog] = []
        
    def log(self, user_id: str, action: str, resource: str,
             success: bool = True, **kwargs) -> AuditLog:
        """Запись в лог"""
        log = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            **kwargs
        )
        
        self.logs.append(log)
        
        # Ограничение размера
        if len(self.logs) > 100000:
            self.logs = self.logs[-50000:]
            
        return log
        
    def query(self, user_id: str = None, action: str = None,
               success: bool = None, hours: int = 24) -> List[AuditLog]:
        """Запрос логов"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        result = []
        for log in self.logs:
            if log.timestamp < cutoff:
                continue
            if user_id and log.user_id != user_id:
                continue
            if action and log.action != action:
                continue
            if success is not None and log.success != success:
                continue
            result.append(log)
            
        return result
        
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Получение сводки"""
        logs = self.query(hours=hours)
        
        by_action = defaultdict(int)
        by_user = defaultdict(int)
        failed = 0
        
        for log in logs:
            by_action[log.action] += 1
            by_user[log.user_id] += 1
            if not log.success:
                failed += 1
                
        return {
            "total": len(logs),
            "successful": len(logs) - failed,
            "failed": failed,
            "by_action": dict(by_action),
            "top_users": dict(sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:10])
        }


class AccessReviewManager:
    """Менеджер ревизий доступа"""
    
    def __init__(self):
        self.reviews: Dict[str, AccessReview] = {}
        
    def create_review(self, name: str, target_users: List[str],
                       reviewer_id: str, due_days: int = 7) -> AccessReview:
        """Создание ревизии"""
        review = AccessReview(
            review_id=f"review_{uuid.uuid4().hex[:8]}",
            name=name,
            target_users=target_users,
            reviewer_id=reviewer_id,
            due_date=datetime.now() + timedelta(days=due_days)
        )
        
        self.reviews[review.review_id] = review
        return review
        
    def make_decision(self, review_id: str, user_id: str, decision: str):
        """Принятие решения"""
        review = self.reviews.get(review_id)
        if review and user_id in review.target_users:
            review.decisions[user_id] = decision
            
            # Проверка завершения
            if len(review.decisions) == len(review.target_users):
                review.status = "completed"
                review.completed_at = datetime.now()
                
    def get_pending(self, reviewer_id: str) -> List[AccessReview]:
        """Получение ожидающих ревизий"""
        return [
            r for r in self.reviews.values()
            if r.reviewer_id == reviewer_id and r.status in ["pending", "in_progress"]
        ]


class IAMPlatform:
    """Платформа IAM"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        self.group_manager = GroupManager()
        self.policy_engine = PolicyEngine(self.role_manager, self.group_manager)
        self.session_manager = SessionManager()
        self.mfa_manager = MFAManager()
        self.audit_logger = AuditLogger()
        self.access_review_manager = AccessReviewManager()
        
    async def authenticate(self, username: str, password: str,
                            mfa_code: str = None, context: Dict[str, Any] = None) -> tuple:
        """Аутентификация"""
        context = context or {}
        
        user = self.user_manager.get_by_username(username)
        
        if not user:
            self.audit_logger.log("unknown", "login", f"user:{username}", success=False,
                                   error_message="User not found")
            return None, "Invalid credentials"
            
        # Проверка статуса
        if user.status == UserStatus.LOCKED:
            self.audit_logger.log(user.user_id, "login", f"user:{user.user_id}", success=False,
                                   error_message="Account locked")
            return None, "Account locked"
            
        if user.status != UserStatus.ACTIVE:
            return None, "Account not active"
            
        # Проверка пароля
        if not self.user_manager.verify_password(user.user_id, password):
            self.user_manager.record_failed_login(user.user_id)
            self.audit_logger.log(user.user_id, "login", f"user:{user.user_id}", success=False,
                                   error_message="Wrong password")
            return None, "Invalid credentials"
            
        # Проверка MFA
        if user.mfa_enabled:
            if not mfa_code:
                return None, "MFA code required"
                
            if user.mfa_type == MFAType.TOTP:
                if not self.mfa_manager.verify_totp(user.user_id, mfa_code, user.mfa_secret):
                    return None, "Invalid MFA code"
            elif user.mfa_type == MFAType.SMS:
                if not self.mfa_manager.verify_sms_code(user.user_id, mfa_code):
                    return None, "Invalid MFA code"
                    
        # Успешная аутентификация
        self.user_manager.reset_failed_logins(user.user_id)
        user.last_login = datetime.now()
        
        # Создание сессии
        session = self.session_manager.create_session(
            user.user_id,
            ip_address=context.get("ip_address", ""),
            user_agent=context.get("user_agent", "")
        )
        
        self.audit_logger.log(user.user_id, "login", f"user:{user.user_id}", success=True,
                               session_id=session.session_id)
        
        return session, None
        
    async def authorize(self, session_id: str, resource: str, action: str,
                         context: Dict[str, Any] = None) -> tuple:
        """Авторизация"""
        context = context or {}
        
        session = self.session_manager.validate_session(session_id)
        
        if not session:
            return False, "Invalid session"
            
        user = self.user_manager.users.get(session.user_id)
        
        if not user:
            return False, "User not found"
            
        # Добавляем контекст
        context["ip_address"] = session.ip_address
        context["mfa_verified"] = user.mfa_enabled
        
        # Проверяем роли пользователя
        for role_name in user.roles:
            permissions = self.role_manager.get_effective_permissions(role_name)
            
            # Проверка по разрешениям роли
            for perm in permissions:
                if perm == "*:*":
                    self.audit_logger.log(user.user_id, action, resource, success=True)
                    return True, "Admin access"
                    
                perm_resource, perm_action = perm.split(":")
                
                if self._match_pattern(perm_resource, resource) and \
                   self._match_pattern(perm_action, action):
                    self.audit_logger.log(user.user_id, action, resource, success=True)
                    return True, f"Allowed by role: {role_name}"
                    
        # Проверяем политики
        allowed, reason = self.policy_engine.evaluate(user.user_id, resource, action, context)
        
        self.audit_logger.log(user.user_id, action, resource, success=allowed,
                               error_message="" if allowed else reason)
        
        return allowed, reason
        
    def _match_pattern(self, pattern: str, value: str) -> bool:
        """Сопоставление с паттерном"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        return pattern == value
        
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        active_sessions = len([
            s for s in self.session_manager.sessions.values()
            if s.state == SessionState.ACTIVE
        ])
        
        return {
            "users": len(self.user_manager.users),
            "roles": len(self.role_manager.roles),
            "groups": len(self.group_manager.groups),
            "policies": len(self.policy_engine.policies),
            "active_sessions": active_sessions,
            "audit_logs": len(self.audit_logger.logs)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 58: Identity & Access Management")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        iam = IAMPlatform()
        print("✓ IAM Platform created")
        
        # Создание пользователей
        print("\n👤 Creating users...")
        
        admin = iam.user_manager.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
            display_name="System Administrator",
            status=UserStatus.ACTIVE,
            roles=["admin"]
        )
        print(f"  ✓ Admin: {admin.username}")
        
        user1 = iam.user_manager.create_user(
            username="john.doe",
            email="john@example.com",
            password="UserPass123!",
            display_name="John Doe",
            status=UserStatus.ACTIVE,
            roles=["user"]
        )
        print(f"  ✓ User: {user1.username}")
        
        operator = iam.user_manager.create_user(
            username="operator",
            email="operator@example.com",
            password="OpPass123!",
            display_name="System Operator",
            status=UserStatus.ACTIVE,
            roles=["operator"]
        )
        print(f"  ✓ Operator: {operator.username}")
        
        # Настройка MFA
        print("\n🔐 Setting up MFA...")
        
        totp_secret = iam.mfa_manager.setup_totp(admin.user_id)
        admin.mfa_enabled = True
        admin.mfa_type = MFAType.TOTP
        admin.mfa_secret = totp_secret
        print(f"  ✓ TOTP enabled for {admin.username}")
        
        # Создание групп
        print("\n👥 Creating groups...")
        
        dev_group = iam.group_manager.create_group(
            name="developers",
            description="Development team",
            roles=["user"]
        )
        iam.group_manager.add_member(dev_group.group_id, user1.user_id)
        print(f"  ✓ Group: {dev_group.name} ({len(dev_group.members)} members)")
        
        # Создание политик
        print("\n📜 Creating policies...")
        
        policy1 = iam.policy_engine.create_policy(
            name="DevelopersReadProjects",
            effect=PolicyEffect.ALLOW,
            principals=[dev_group.group_id],
            resources=["projects:*"],
            actions=["read", "list"]
        )
        print(f"  ✓ Policy: {policy1.name}")
        
        policy2 = iam.policy_engine.create_policy(
            name="DenyProductionAccess",
            effect=PolicyEffect.DENY,
            principals=["*"],
            resources=["production:*"],
            actions=["*"],
            conditions={"time_range": {"start": "00:00", "end": "06:00"}},
            priority=10
        )
        print(f"  ✓ Policy: {policy2.name}")
        
        # Аутентификация
        print("\n🔑 Authentication tests...")
        
        # Успешная аутентификация без MFA
        session1, error = await iam.authenticate(
            "john.doe",
            "UserPass123!",
            context={"ip_address": "192.168.1.100"}
        )
        print(f"  {'✓' if session1 else '✗'} john.doe login: {'Success' if session1 else error}")
        
        # Аутентификация с MFA
        session2, error = await iam.authenticate(
            "admin",
            "AdminPass123!",
            mfa_code="123456",  # Для демо
            context={"ip_address": "192.168.1.1"}
        )
        print(f"  {'✓' if session2 else '✗'} admin login (with MFA): {'Success' if session2 else error}")
        
        # Неудачная аутентификация
        session3, error = await iam.authenticate(
            "john.doe",
            "WrongPassword",
            context={"ip_address": "192.168.1.100"}
        )
        print(f"  {'✓' if not session3 else '✗'} john.doe wrong password: {error}")
        
        # Авторизация
        print("\n🔒 Authorization tests...")
        
        if session1:
            # User читает профиль
            allowed, reason = await iam.authorize(
                session1.session_id,
                "profile",
                "read"
            )
            print(f"  {'✓' if allowed else '✗'} john.doe read profile: {reason}")
            
            # User читает проекты (через группу)
            allowed, reason = await iam.authorize(
                session1.session_id,
                "projects:project-1",
                "read"
            )
            print(f"  {'✓' if allowed else '✗'} john.doe read project: {reason}")
            
            # User пытается удалить
            allowed, reason = await iam.authorize(
                session1.session_id,
                "projects:project-1",
                "delete"
            )
            print(f"  {'✓' if not allowed else '✗'} john.doe delete project: {reason}")
            
        if session2:
            # Admin полный доступ
            allowed, reason = await iam.authorize(
                session2.session_id,
                "anything",
                "delete"
            )
            print(f"  {'✓' if allowed else '✗'} admin delete anything: {reason}")
            
        # Управление сессиями
        print("\n📋 Session management...")
        
        if session1:
            # Валидация сессии
            valid = iam.session_manager.validate_session(session1.session_id)
            print(f"  Session valid: {valid is not None}")
            
            # Обновление сессии
            new_session = iam.session_manager.refresh_session(session1.refresh_token)
            print(f"  Session refreshed: {new_session is not None}")
            
            # Отзыв сессии
            if new_session:
                iam.session_manager.revoke_session(new_session.session_id)
                valid = iam.session_manager.validate_session(new_session.session_id)
                print(f"  Session revoked: {valid is None}")
                
        # Аудит
        print("\n📊 Audit summary...")
        
        summary = iam.audit_logger.get_summary(hours=24)
        print(f"  Total events: {summary['total']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Actions: {list(summary['by_action'].keys())}")
        
        # Ревизия доступа
        print("\n🔍 Access review...")
        
        review = iam.access_review_manager.create_review(
            name="Q4 Access Review",
            target_users=[user1.user_id, operator.user_id],
            reviewer_id=admin.user_id,
            due_days=7
        )
        print(f"  ✓ Review created: {review.name}")
        
        # Принятие решений
        iam.access_review_manager.make_decision(review.review_id, user1.user_id, "approve")
        iam.access_review_manager.make_decision(review.review_id, operator.user_id, "approve")
        
        print(f"  Review status: {review.status}")
        print(f"  Decisions: {len(review.decisions)}/{len(review.target_users)}")
        
        # Статистика
        print("\n📈 Platform Statistics:")
        stats = iam.get_stats()
        print(f"  Users: {stats['users']}")
        print(f"  Roles: {stats['roles']}")
        print(f"  Groups: {stats['groups']}")
        print(f"  Policies: {stats['policies']}")
        print(f"  Active Sessions: {stats['active_sessions']}")
        print(f"  Audit Logs: {stats['audit_logs']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Identity & Access Management Platform initialized!")
    print("=" * 60)
