#!/usr/bin/env python3
"""
Server Init - Iteration 362: ChatOps Platform
Платформа ChatOps для автоматизации через чат

Функционал:
- Bot Integration - интеграция ботов
- Command Framework - фреймворк команд
- Workflow Automation - автоматизация workflow
- Interactive Messages - интерактивные сообщения
- Channel Management - управление каналами
- Permission System - система прав
- Audit Logging - журнал аудита
- Plugin System - система плагинов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
import uuid
import re


class PlatformType(Enum):
    """Тип платформы"""
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    MATTERMOST = "mattermost"
    TELEGRAM = "telegram"


class MessageType(Enum):
    """Тип сообщения"""
    TEXT = "text"
    COMMAND = "command"
    INTERACTIVE = "interactive"
    FILE = "file"
    REACTION = "reaction"
    THREAD_REPLY = "thread_reply"


class CommandType(Enum):
    """Тип команды"""
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    STATUS = "status"
    SCALE = "scale"
    RESTART = "restart"
    CONFIG = "config"
    ALERT = "alert"
    ONCALL = "oncall"
    INCIDENT = "incident"
    CUSTOM = "custom"


class ExecutionStatus(Enum):
    """Статус выполнения"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class PermissionLevel(Enum):
    """Уровень прав"""
    READ = "read"
    EXECUTE = "execute"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class WorkflowTrigger(Enum):
    """Триггер workflow"""
    COMMAND = "command"
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"


class WorkflowStatus(Enum):
    """Статус workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class User:
    """Пользователь"""
    user_id: str
    
    # Info
    username: str = ""
    display_name: str = ""
    email: str = ""
    
    # Platform
    platform: PlatformType = PlatformType.SLACK
    platform_user_id: str = ""
    
    # Permissions
    permission_level: PermissionLevel = PermissionLevel.READ
    groups: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_active_at: Optional[datetime] = None


@dataclass
class Channel:
    """Канал"""
    channel_id: str
    
    # Info
    name: str = ""
    description: str = ""
    
    # Platform
    platform: PlatformType = PlatformType.SLACK
    platform_channel_id: str = ""
    
    # Type
    is_private: bool = False
    is_archive: bool = False
    
    # Configuration
    allowed_commands: List[str] = field(default_factory=list)
    notification_types: List[str] = field(default_factory=list)
    
    # Members
    members: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Command:
    """Команда"""
    command_id: str
    
    # Identity
    name: str = ""
    aliases: List[str] = field(default_factory=list)
    
    # Type
    command_type: CommandType = CommandType.CUSTOM
    
    # Description
    description: str = ""
    usage: str = ""
    examples: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    
    # Permissions
    required_permission: PermissionLevel = PermissionLevel.EXECUTE
    allowed_channels: List[str] = field(default_factory=list)
    allowed_groups: List[str] = field(default_factory=list)
    
    # Handler
    handler_name: str = ""
    
    # Flags
    is_enabled: bool = True
    requires_confirmation: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    
    # Type
    message_type: MessageType = MessageType.TEXT
    
    # Content
    text: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context
    channel_id: str = ""
    user_id: str = ""
    thread_ts: str = ""
    
    # Platform
    platform: PlatformType = PlatformType.SLACK
    platform_message_id: str = ""
    
    # Reactions
    reactions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CommandExecution:
    """Выполнение команды"""
    execution_id: str
    
    # Command
    command_id: str = ""
    command_name: str = ""
    
    # Context
    user_id: str = ""
    channel_id: str = ""
    message_id: str = ""
    
    # Input
    raw_input: str = ""
    parsed_args: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Output
    output: str = ""
    error: str = ""
    
    # Duration
    duration_ms: int = 0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class InteractiveAction:
    """Интерактивное действие"""
    action_id: str
    
    # Type
    action_type: str = "button"  # button, select, dialog
    
    # Value
    value: str = ""
    
    # Context
    user_id: str = ""
    channel_id: str = ""
    message_id: str = ""
    
    # Callback
    callback_id: str = ""
    
    # Status
    status: str = "pending"
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowStep:
    """Шаг workflow"""
    step_id: str
    
    # Order
    order: int = 0
    
    # Command or Action
    command_name: str = ""
    action_type: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Conditions
    condition: str = ""
    
    # Status
    status: WorkflowStatus = WorkflowStatus.PENDING
    
    # Output
    output: Any = None
    error: str = ""


@dataclass
class Workflow:
    """Workflow"""
    workflow_id: str
    
    # Info
    name: str = ""
    description: str = ""
    
    # Trigger
    trigger: WorkflowTrigger = WorkflowTrigger.COMMAND
    trigger_pattern: str = ""
    
    # Steps
    steps: List[WorkflowStep] = field(default_factory=list)
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    
    # Context
    started_by: str = ""
    channel_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowTemplate:
    """Шаблон workflow"""
    template_id: str
    
    # Info
    name: str = ""
    description: str = ""
    
    # Steps
    step_templates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Variables
    required_variables: List[str] = field(default_factory=list)
    
    # Permissions
    required_permission: PermissionLevel = PermissionLevel.EXECUTE
    
    # Usage
    usage_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Plugin:
    """Плагин"""
    plugin_id: str
    
    # Info
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    
    # Commands
    commands: List[str] = field(default_factory=list)
    
    # Hooks
    hooks: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class AuditLog:
    """Запись аудита"""
    log_id: str
    
    # Event
    event_type: str = ""
    action: str = ""
    
    # Actor
    user_id: str = ""
    username: str = ""
    
    # Context
    channel_id: str = ""
    command_name: str = ""
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "success"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChatOpsMetrics:
    """Метрики ChatOps"""
    metrics_id: str
    
    # Commands
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    
    # Messages
    total_messages: int = 0
    
    # Workflows
    total_workflows: int = 0
    active_workflows: int = 0
    
    # Users
    active_users: int = 0
    
    # Performance
    avg_execution_time_ms: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class ChatOpsPlatform:
    """Платформа ChatOps"""
    
    def __init__(self, platform_name: str = "chatops"):
        self.platform_name = platform_name
        self.users: Dict[str, User] = {}
        self.channels: Dict[str, Channel] = {}
        self.commands: Dict[str, Command] = {}
        self.messages: Dict[str, Message] = {}
        self.executions: Dict[str, CommandExecution] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.plugins: Dict[str, Plugin] = {}
        self.audit_logs: List[AuditLog] = []
        self.interactive_actions: Dict[str, InteractiveAction] = {}
        
        # Command handlers
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[str]]] = {}
        
    async def register_user(self, username: str,
                           display_name: str = "",
                           email: str = "",
                           platform: PlatformType = PlatformType.SLACK,
                           platform_user_id: str = "",
                           permission_level: PermissionLevel = PermissionLevel.READ) -> User:
        """Регистрация пользователя"""
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:8]}",
            username=username,
            display_name=display_name or username,
            email=email,
            platform=platform,
            platform_user_id=platform_user_id,
            permission_level=permission_level
        )
        
        self.users[user.user_id] = user
        
        await self._log_audit("user_registered", "register", user.user_id, details={"username": username})
        
        return user
        
    async def create_channel(self, name: str,
                            description: str = "",
                            platform: PlatformType = PlatformType.SLACK,
                            platform_channel_id: str = "",
                            is_private: bool = False,
                            allowed_commands: List[str] = None,
                            members: List[str] = None) -> Channel:
        """Создание канала"""
        channel = Channel(
            channel_id=f"ch_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            platform=platform,
            platform_channel_id=platform_channel_id,
            is_private=is_private,
            allowed_commands=allowed_commands or [],
            members=members or []
        )
        
        self.channels[channel.channel_id] = channel
        
        return channel
        
    async def register_command(self, name: str,
                              command_type: CommandType = CommandType.CUSTOM,
                              description: str = "",
                              usage: str = "",
                              parameters: List[Dict[str, Any]] = None,
                              required_permission: PermissionLevel = PermissionLevel.EXECUTE,
                              handler: Callable[[Dict[str, Any]], Awaitable[str]] = None,
                              requires_confirmation: bool = False) -> Command:
        """Регистрация команды"""
        command = Command(
            command_id=f"cmd_{uuid.uuid4().hex[:8]}",
            name=name,
            command_type=command_type,
            description=description,
            usage=usage,
            parameters=parameters or [],
            required_permission=required_permission,
            handler_name=f"handler_{name}",
            requires_confirmation=requires_confirmation
        )
        
        self.commands[command.command_id] = command
        
        if handler:
            self._handlers[command.handler_name] = handler
            
        return command
        
    async def send_message(self, channel_id: str,
                          text: str,
                          user_id: str = "",
                          message_type: MessageType = MessageType.TEXT,
                          attachments: List[Dict[str, Any]] = None,
                          blocks: List[Dict[str, Any]] = None,
                          thread_ts: str = "") -> Message:
        """Отправка сообщения"""
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            text=text,
            attachments=attachments or [],
            blocks=blocks or [],
            channel_id=channel_id,
            user_id=user_id,
            thread_ts=thread_ts,
            platform_message_id=f"pm_{uuid.uuid4().hex[:8]}"
        )
        
        self.messages[message.message_id] = message
        
        return message
        
    async def process_message(self, channel_id: str,
                             user_id: str,
                             text: str) -> Optional[CommandExecution]:
        """Обработка входящего сообщения"""
        # Check if it's a command
        if not text.startswith("/") and not text.startswith("!"):
            # Store as regular message
            await self.send_message(channel_id, text, user_id)
            return None
            
        # Parse command
        parts = text[1:].split()
        command_name = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Find command
        command = None
        for cmd in self.commands.values():
            if cmd.name == command_name or command_name in cmd.aliases:
                command = cmd
                break
                
        if not command:
            return None
            
        # Check permissions
        user = self.users.get(user_id)
        if not user or user.permission_level.value < command.required_permission.value:
            return None
            
        # Execute command
        return await self.execute_command(command.command_id, user_id, channel_id, args)
        
    async def execute_command(self, command_id: str,
                             user_id: str,
                             channel_id: str,
                             args: List[str] = None) -> CommandExecution:
        """Выполнение команды"""
        command = self.commands.get(command_id)
        
        execution = CommandExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            command_id=command_id,
            command_name=command.name if command else "",
            user_id=user_id,
            channel_id=channel_id,
            raw_input=" ".join(args) if args else "",
            status=ExecutionStatus.RUNNING
        )
        
        start_time = datetime.now()
        
        try:
            # Get handler
            handler = self._handlers.get(command.handler_name) if command else None
            
            if handler:
                result = await handler({"args": args, "user_id": user_id, "channel_id": channel_id})
                execution.output = result
                execution.status = ExecutionStatus.SUCCESS
            else:
                # Default handler
                await asyncio.sleep(0.05)  # Simulate work
                execution.output = f"Command '{command.name if command else 'unknown'}' executed with args: {args}"
                execution.status = ExecutionStatus.SUCCESS
                
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            
        execution.completed_at = datetime.now()
        execution.duration_ms = int((execution.completed_at - start_time).total_seconds() * 1000)
        
        self.executions[execution.execution_id] = execution
        
        # Audit log
        await self._log_audit(
            "command_executed",
            command.name if command else "unknown",
            user_id,
            channel_id=channel_id,
            command_name=command.name if command else "",
            details={"args": args, "status": execution.status.value}
        )
        
        return execution
        
    async def create_interactive_message(self, channel_id: str,
                                        text: str,
                                        blocks: List[Dict[str, Any]]) -> Message:
        """Создание интерактивного сообщения"""
        return await self.send_message(
            channel_id,
            text,
            message_type=MessageType.INTERACTIVE,
            blocks=blocks
        )
        
    async def handle_interactive_action(self, action_id: str,
                                       user_id: str,
                                       channel_id: str,
                                       value: str,
                                       callback_id: str = "") -> InteractiveAction:
        """Обработка интерактивного действия"""
        action = InteractiveAction(
            action_id=action_id,
            value=value,
            user_id=user_id,
            channel_id=channel_id,
            callback_id=callback_id,
            status="processed"
        )
        
        self.interactive_actions[action_id] = action
        
        return action
        
    async def create_workflow_template(self, name: str,
                                       description: str = "",
                                       step_templates: List[Dict[str, Any]] = None,
                                       required_variables: List[str] = None) -> WorkflowTemplate:
        """Создание шаблона workflow"""
        template = WorkflowTemplate(
            template_id=f"wft_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            step_templates=step_templates or [],
            required_variables=required_variables or []
        )
        
        self.workflow_templates[template.template_id] = template
        
        return template
        
    async def start_workflow(self, template_id: str,
                            user_id: str,
                            channel_id: str,
                            variables: Dict[str, Any] = None) -> Workflow:
        """Запуск workflow из шаблона"""
        template = self.workflow_templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        # Create steps from template
        steps = []
        for i, step_template in enumerate(template.step_templates):
            step = WorkflowStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                order=i,
                command_name=step_template.get("command", ""),
                action_type=step_template.get("action", ""),
                parameters=step_template.get("parameters", {}),
                condition=step_template.get("condition", "")
            )
            steps.append(step)
            
        workflow = Workflow(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            name=template.name,
            description=template.description,
            trigger=WorkflowTrigger.COMMAND,
            steps=steps,
            variables=variables or {},
            started_by=user_id,
            channel_id=channel_id,
            started_at=datetime.now(),
            status=WorkflowStatus.RUNNING
        )
        
        self.workflows[workflow.workflow_id] = workflow
        
        # Increment usage count
        template.usage_count += 1
        
        # Execute workflow
        await self._execute_workflow(workflow)
        
        return workflow
        
    async def _execute_workflow(self, workflow: Workflow):
        """Выполнение workflow"""
        for step in workflow.steps:
            workflow.current_step = step.order
            step.status = WorkflowStatus.RUNNING
            
            try:
                # Simulate step execution
                await asyncio.sleep(0.02)
                
                # Execute command if specified
                if step.command_name:
                    for cmd in self.commands.values():
                        if cmd.name == step.command_name:
                            exec_result = await self.execute_command(
                                cmd.command_id,
                                workflow.started_by,
                                workflow.channel_id,
                                []
                            )
                            step.output = exec_result.output
                            break
                else:
                    step.output = f"Step {step.order + 1} completed"
                    
                step.status = WorkflowStatus.COMPLETED
                
            except Exception as e:
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
                workflow.status = WorkflowStatus.FAILED
                return
                
        workflow.status = WorkflowStatus.COMPLETED
        workflow.completed_at = datetime.now()
        
    async def register_plugin(self, name: str,
                             description: str = "",
                             version: str = "1.0.0",
                             author: str = "",
                             commands: List[str] = None,
                             config: Dict[str, Any] = None) -> Plugin:
        """Регистрация плагина"""
        plugin = Plugin(
            plugin_id=f"plg_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            version=version,
            author=author,
            commands=commands or [],
            config=config or {}
        )
        
        self.plugins[plugin.plugin_id] = plugin
        
        return plugin
        
    async def _log_audit(self, event_type: str,
                        action: str,
                        user_id: str,
                        channel_id: str = "",
                        command_name: str = "",
                        details: Dict[str, Any] = None):
        """Запись в журнал аудита"""
        user = self.users.get(user_id)
        
        log = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=user.username if user else "",
            channel_id=channel_id,
            command_name=command_name,
            details=details or {}
        )
        
        self.audit_logs.append(log)
        
    async def collect_metrics(self) -> ChatOpsMetrics:
        """Сбор метрик"""
        successful_commands = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.SUCCESS)
        failed_commands = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED)
        active_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.RUNNING)
        
        # Calculate average execution time
        execution_times = [e.duration_ms for e in self.executions.values() if e.duration_ms > 0]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        # Count active users (last 24 hours)
        now = datetime.now()
        active_users = sum(
            1 for u in self.users.values()
            if u.last_active_at and (now - u.last_active_at).total_seconds() < 86400
        )
        
        return ChatOpsMetrics(
            metrics_id=f"com_{uuid.uuid4().hex[:8]}",
            total_commands=len(self.executions),
            successful_commands=successful_commands,
            failed_commands=failed_commands,
            total_messages=len(self.messages),
            total_workflows=len(self.workflows),
            active_workflows=active_workflows,
            active_users=active_users,
            avg_execution_time_ms=avg_time
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        successful_commands = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.SUCCESS)
        failed_commands = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED)
        active_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.RUNNING)
        enabled_plugins = sum(1 for p in self.plugins.values() if p.is_enabled)
        
        commands_by_type = {}
        for cmd in self.commands.values():
            cmd_type = cmd.command_type.value
            commands_by_type[cmd_type] = commands_by_type.get(cmd_type, 0) + 1
            
        return {
            "total_users": len(self.users),
            "total_channels": len(self.channels),
            "total_commands": len(self.commands),
            "commands_by_type": commands_by_type,
            "total_executions": len(self.executions),
            "successful_executions": successful_commands,
            "failed_executions": failed_commands,
            "total_messages": len(self.messages),
            "total_workflows": len(self.workflows),
            "active_workflows": active_workflows,
            "workflow_templates": len(self.workflow_templates),
            "total_plugins": len(self.plugins),
            "enabled_plugins": enabled_plugins,
            "audit_logs": len(self.audit_logs)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 362: ChatOps Platform")
    print("=" * 60)
    
    platform = ChatOpsPlatform(platform_name="enterprise-chatops")
    print("✓ ChatOps Platform initialized")
    
    # Register Users
    print("\n👥 Registering Users...")
    
    users_data = [
        ("admin", "Admin User", "admin@example.com", PermissionLevel.SUPER_ADMIN),
        ("john.smith", "John Smith", "john@example.com", PermissionLevel.ADMIN),
        ("jane.doe", "Jane Doe", "jane@example.com", PermissionLevel.EXECUTE),
        ("bob.wilson", "Bob Wilson", "bob@example.com", PermissionLevel.EXECUTE),
        ("alice.brown", "Alice Brown", "alice@example.com", PermissionLevel.READ),
        ("dev.team", "Dev Team Bot", "devteam@example.com", PermissionLevel.EXECUTE)
    ]
    
    users = []
    for username, display, email, perm in users_data:
        user = await platform.register_user(username, display, email, permission_level=perm)
        users.append(user)
        print(f"  👤 {display} ({perm.value})")
        
    # Create Channels
    print("\n📢 Creating Channels...")
    
    channels_data = [
        ("#deployments", "Deployment notifications and commands", False, ["deploy", "rollback", "status"]),
        ("#alerts", "Alert notifications", False, ["alert", "ack", "silence"]),
        ("#incidents", "Incident management", False, ["incident", "oncall", "escalate"]),
        ("#ops-general", "General operations", False, []),
        ("#private-ops", "Private ops channel", True, ["deploy", "config"])
    ]
    
    channels = []
    for name, desc, is_private, cmds in channels_data:
        channel = await platform.create_channel(
            name, desc, 
            is_private=is_private, 
            allowed_commands=cmds,
            members=[u.user_id for u in users[:4]]
        )
        channels.append(channel)
        print(f"  📢 {name} ({len(cmds)} commands allowed)")
        
    # Register Commands
    print("\n⚡ Registering Commands...")
    
    # Define command handlers
    async def deploy_handler(ctx):
        service = ctx.get("args", ["api-service"])[0] if ctx.get("args") else "api-service"
        return f"Deploying {service}... Done! ✅"
        
    async def status_handler(ctx):
        return "All services operational ✅"
        
    async def scale_handler(ctx):
        args = ctx.get("args", [])
        service = args[0] if args else "api-service"
        replicas = args[1] if len(args) > 1 else "3"
        return f"Scaled {service} to {replicas} replicas"
        
    commands_data = [
        ("deploy", CommandType.DEPLOY, "Deploy a service", "/deploy <service> [version]", PermissionLevel.EXECUTE, deploy_handler, True),
        ("rollback", CommandType.ROLLBACK, "Rollback deployment", "/rollback <service> [version]", PermissionLevel.EXECUTE, None, True),
        ("status", CommandType.STATUS, "Check service status", "/status [service]", PermissionLevel.READ, status_handler, False),
        ("scale", CommandType.SCALE, "Scale a service", "/scale <service> <replicas>", PermissionLevel.EXECUTE, scale_handler, True),
        ("restart", CommandType.RESTART, "Restart a service", "/restart <service>", PermissionLevel.EXECUTE, None, True),
        ("config", CommandType.CONFIG, "View/update config", "/config <service> [key] [value]", PermissionLevel.ADMIN, None, False),
        ("alert", CommandType.ALERT, "Manage alerts", "/alert <action> [id]", PermissionLevel.EXECUTE, None, False),
        ("oncall", CommandType.ONCALL, "View on-call schedule", "/oncall [team]", PermissionLevel.READ, None, False),
        ("incident", CommandType.INCIDENT, "Manage incidents", "/incident <action> [id]", PermissionLevel.EXECUTE, None, False),
        ("help", CommandType.CUSTOM, "Show help", "/help [command]", PermissionLevel.READ, None, False)
    ]
    
    commands = []
    for name, cmd_type, desc, usage, perm, handler, confirm in commands_data:
        cmd = await platform.register_command(
            name, cmd_type, desc, usage,
            required_permission=perm,
            handler=handler,
            requires_confirmation=confirm
        )
        commands.append(cmd)
        print(f"  ⚡ /{name} ({cmd_type.value}, {perm.value})")
        
    # Register Plugins
    print("\n🔌 Registering Plugins...")
    
    plugins_data = [
        ("kubernetes-plugin", "Kubernetes integration", "2.1.0", "Platform Team", ["kubectl", "k8s-status", "pods"]),
        ("aws-plugin", "AWS integration", "1.5.0", "Cloud Team", ["ec2", "s3", "lambda"]),
        ("github-plugin", "GitHub integration", "3.0.1", "DevOps Team", ["pr", "issue", "release"]),
        ("jira-plugin", "Jira integration", "1.2.0", "Product Team", ["ticket", "sprint", "board"]),
        ("datadog-plugin", "Datadog integration", "2.0.0", "SRE Team", ["metrics", "monitors", "dashboards"])
    ]
    
    plugins = []
    for name, desc, version, author, cmds in plugins_data:
        plugin = await platform.register_plugin(name, desc, version, author, cmds)
        plugins.append(plugin)
        print(f"  🔌 {name} v{version} ({len(cmds)} commands)")
        
    # Create Workflow Templates
    print("\n📋 Creating Workflow Templates...")
    
    templates_data = [
        ("production-deploy", "Production deployment workflow", [
            {"command": "status", "parameters": {"service": "all"}},
            {"command": "deploy", "parameters": {"environment": "production"}},
            {"command": "status", "parameters": {"service": "all"}}
        ], ["service", "version"]),
        ("incident-response", "Incident response workflow", [
            {"command": "incident", "action": "create"},
            {"command": "alert", "action": "acknowledge"},
            {"command": "oncall", "action": "notify"}
        ], ["incident_id", "severity"]),
        ("scale-up", "Auto scale up workflow", [
            {"command": "status", "parameters": {}},
            {"command": "scale", "parameters": {"replicas": "increase"}}
        ], ["service"])
    ]
    
    templates = []
    for name, desc, steps, vars in templates_data:
        template = await platform.create_workflow_template(name, desc, steps, vars)
        templates.append(template)
        print(f"  📋 {name} ({len(steps)} steps)")
        
    # Execute Commands
    print("\n🚀 Executing Commands...")
    
    executions_data = [
        (users[1].user_id, channels[0].channel_id, "/deploy api-service v2.1.0"),
        (users[2].user_id, channels[0].channel_id, "/status api-service"),
        (users[1].user_id, channels[0].channel_id, "/scale payment-service 5"),
        (users[2].user_id, channels[1].channel_id, "/alert list"),
        (users[0].user_id, channels[0].channel_id, "/deploy order-service v1.5.0"),
        (users[3].user_id, channels[3].channel_id, "/status"),
        (users[1].user_id, channels[2].channel_id, "/incident create critical"),
        (users[2].user_id, channels[0].channel_id, "/rollback api-service"),
        (users[0].user_id, channels[4].channel_id, "/config database connection_pool 100"),
        (users[1].user_id, channels[0].channel_id, "/restart notification-service")
    ]
    
    executions = []
    for user_id, channel_id, text in executions_data:
        exec_result = await platform.process_message(channel_id, user_id, text)
        if exec_result:
            executions.append(exec_result)
            status = "✓" if exec_result.status == ExecutionStatus.SUCCESS else "✗"
            print(f"  {status} {text[:40]}... ({exec_result.duration_ms}ms)")
            
    # Send Messages
    print("\n💬 Sending Messages...")
    
    messages_data = [
        (channels[0].channel_id, "🚀 Deployment started for api-service v2.1.0", users[1].user_id),
        (channels[0].channel_id, "✅ Deployment completed successfully", users[1].user_id),
        (channels[1].channel_id, "🔔 Alert: High CPU usage on payment-service-1", ""),
        (channels[2].channel_id, "🔥 Incident INC-001 created: Database connection issues", users[1].user_id),
        (channels[3].channel_id, "📊 Daily status report generated", "")
    ]
    
    for channel_id, text, user_id in messages_data:
        await platform.send_message(channel_id, text, user_id)
        
    print(f"  💬 Sent {len(messages_data)} messages")
    
    # Create Interactive Messages
    print("\n🎯 Creating Interactive Messages...")
    
    interactive_blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Approve deployment?"}
        },
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": "Approve", "style": "primary", "action_id": "approve"},
                {"type": "button", "text": "Reject", "style": "danger", "action_id": "reject"}
            ]
        }
    ]
    
    await platform.create_interactive_message(
        channels[0].channel_id,
        "Deployment approval required",
        interactive_blocks
    )
    print("  🎯 Created deployment approval message")
    
    # Handle Interactive Actions
    await platform.handle_interactive_action(
        f"act_{uuid.uuid4().hex[:8]}",
        users[1].user_id,
        channels[0].channel_id,
        "approve",
        "deployment_approval"
    )
    print("  ✓ Handled approval action")
    
    # Start Workflows
    print("\n🔄 Starting Workflows...")
    
    workflows = []
    for template in templates[:2]:
        workflow = await platform.start_workflow(
            template.template_id,
            users[1].user_id,
            channels[0].channel_id,
            {"service": "api-service", "version": "2.1.0"}
        )
        workflows.append(workflow)
        print(f"  🔄 {workflow.name}: {workflow.status.value}")
        
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Commands Dashboard
    print("\n⚡ Registered Commands:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Command       │ Type        │ Permission    │ Confirmation  │ Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for cmd in commands:
        name = f"/{cmd.name}"[:13].ljust(13)
        cmd_type = cmd.command_type.value[:11].ljust(11)
        perm = cmd.required_permission.value[:13].ljust(13)
        confirm = "Yes" if cmd.requires_confirmation else "No"
        confirm = confirm.ljust(13)
        desc = cmd.description[:118].ljust(118)
        
        print(f"  │ {name} │ {cmd_type} │ {perm} │ {confirm} │ {desc} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Executions Dashboard
    print("\n🚀 Recent Executions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Command       │ Status      │ Duration    │ User                 │ Output                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for exec in executions[:8]:
        name = exec.command_name[:13].ljust(13)
        status = exec.status.value[:11].ljust(11)
        duration = f"{exec.duration_ms}ms"[:11].ljust(11)
        user = platform.users.get(exec.user_id)
        username = user.username[:20] if user else "unknown"
        username = username.ljust(20)
        output = (exec.output or exec.error)[:155].ljust(155)
        
        print(f"  │ {name} │ {status} │ {duration} │ {username} │ {output} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Plugins Dashboard
    print("\n🔌 Plugins:")
    
    for plugin in plugins:
        status = "✓" if plugin.is_enabled else "✗"
        print(f"  {status} {plugin.name} v{plugin.version} - {plugin.description}")
        
    # Workflows Dashboard
    print("\n🔄 Workflows:")
    
    for wf in workflows:
        completed_steps = sum(1 for s in wf.steps if s.status == WorkflowStatus.COMPLETED)
        print(f"  - {wf.name}: {wf.status.value} ({completed_steps}/{len(wf.steps)} steps)")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Users: {stats['total_users']}")
    print(f"  Channels: {stats['total_channels']}")
    print(f"  Commands: {stats['total_commands']}")
    print(f"  Executions: {stats['successful_executions']}/{stats['total_executions']} successful")
    print(f"  Messages: {stats['total_messages']}")
    print(f"  Workflows: {stats['active_workflows']}/{stats['total_workflows']} active")
    print(f"  Plugins: {stats['enabled_plugins']}/{stats['total_plugins']} enabled")
    print(f"  Audit Logs: {stats['audit_logs']}")
    
    # Commands by Type
    print("\n  Commands by Type:")
    for cmd_type, count in stats["commands_by_type"].items():
        bar = "█" * count
        print(f"    {cmd_type:12s} │ {bar} ({count})")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                         ChatOps Platform                           │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Users:                   {stats['total_users']:>12}                      │")
    print(f"│ Total Channels:                {stats['total_channels']:>12}                      │")
    print(f"│ Total Commands:                {stats['total_commands']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Executions:              {stats['total_executions']:>12}                      │")
    print(f"│ Successful:                    {stats['successful_executions']:>12}                      │")
    print(f"│ Failed:                        {stats['failed_executions']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Messages:                {stats['total_messages']:>12}                      │")
    print(f"│ Total Workflows:               {stats['total_workflows']:>12}                      │")
    print(f"│ Active Workflows:              {stats['active_workflows']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Plugins:                 {stats['total_plugins']:>12}                      │")
    print(f"│ Enabled Plugins:               {stats['enabled_plugins']:>12}                      │")
    print(f"│ Avg Exec Time (ms):            {metrics.avg_execution_time_ms:>12.1f}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("ChatOps Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
