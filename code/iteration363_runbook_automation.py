#!/usr/bin/env python3
"""
Server Init - Iteration 363: Runbook Automation Platform
Платформа автоматизации runbook'ов

Функционал:
- Runbook Management - управление runbook'ами
- Step Execution - выполнение шагов
- Parameter Templates - шаблоны параметров
- Conditional Logic - условная логика
- Approval Workflows - workflow одобрения
- Execution History - история выполнения
- Integration Hooks - хуки интеграции
- Audit Trail - аудит действий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
import uuid


class RunbookType(Enum):
    """Тип runbook"""
    DIAGNOSTIC = "diagnostic"
    REMEDIATION = "remediation"
    MAINTENANCE = "maintenance"
    DEPLOYMENT = "deployment"
    INCIDENT = "incident"
    RECOVERY = "recovery"


class RunbookStatus(Enum):
    """Статус runbook"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class StepType(Enum):
    """Тип шага"""
    SCRIPT = "script"
    COMMAND = "command"
    API_CALL = "api_call"
    APPROVAL = "approval"
    MANUAL = "manual"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    NOTIFICATION = "notification"
    DELAY = "delay"


class ExecutionStatus(Enum):
    """Статус выполнения"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class ApprovalStatus(Enum):
    """Статус одобрения"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ALERT = "alert"
    WEBHOOK = "webhook"
    EVENT = "event"


class ParameterType(Enum):
    """Тип параметра"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SECRET = "secret"
    LIST = "list"
    JSON = "json"
    FILE = "file"


@dataclass
class Parameter:
    """Параметр runbook"""
    param_id: str
    
    # Identity
    name: str = ""
    display_name: str = ""
    description: str = ""
    
    # Type
    param_type: ParameterType = ParameterType.STRING
    
    # Validation
    required: bool = False
    default_value: Any = None
    allowed_values: List[Any] = field(default_factory=list)
    validation_regex: str = ""
    
    # Security
    is_sensitive: bool = False


@dataclass
class StepOutput:
    """Вывод шага"""
    output_id: str
    
    # Data
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    
    # Structured output
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Artifacts
    artifacts: List[str] = field(default_factory=list)


@dataclass
class Step:
    """Шаг runbook"""
    step_id: str
    
    # Identity
    name: str = ""
    description: str = ""
    
    # Type
    step_type: StepType = StepType.COMMAND
    
    # Order
    order: int = 0
    
    # Content
    content: str = ""
    script: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Input parameters
    input_mapping: Dict[str, str] = field(default_factory=dict)
    
    # Output
    output_variable: str = ""
    
    # Control flow
    condition: str = ""
    on_failure: str = "fail"  # fail, continue, retry, skip
    retry_count: int = 0
    retry_delay_seconds: int = 30
    timeout_seconds: int = 300
    
    # Approval
    approvers: List[str] = field(default_factory=list)
    approval_timeout_minutes: int = 60
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Runbook:
    """Runbook"""
    runbook_id: str
    
    # Identity
    name: str = ""
    display_name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Type
    runbook_type: RunbookType = RunbookType.REMEDIATION
    
    # Status
    status: RunbookStatus = RunbookStatus.DRAFT
    
    # Parameters
    parameters: List[Parameter] = field(default_factory=list)
    
    # Steps
    steps: List[Step] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Author
    author: str = ""
    owner_team: str = ""
    
    # Triggers
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Settings
    max_concurrent_executions: int = 5
    default_timeout_minutes: int = 60
    
    # Stats
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


@dataclass
class StepExecution:
    """Выполнение шага"""
    execution_id: str
    
    # References
    runbook_execution_id: str = ""
    step_id: str = ""
    step_name: str = ""
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Output
    output: Optional[StepOutput] = None
    
    # Error
    error_message: str = ""
    
    # Duration
    duration_seconds: float = 0.0
    
    # Retries
    retry_attempt: int = 0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class ApprovalRequest:
    """Запрос на одобрение"""
    request_id: str
    
    # References
    runbook_execution_id: str = ""
    step_id: str = ""
    
    # Approvers
    approvers: List[str] = field(default_factory=list)
    approved_by: str = ""
    rejected_by: str = ""
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    
    # Comment
    comment: str = ""
    
    # Timeout
    expires_at: datetime = field(default_factory=datetime.now)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class RunbookExecution:
    """Выполнение runbook"""
    execution_id: str
    
    # References
    runbook_id: str = ""
    runbook_name: str = ""
    runbook_version: str = ""
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    triggered_by: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Progress
    current_step: int = 0
    total_steps: int = 0
    
    # Step executions
    step_executions: List[StepExecution] = field(default_factory=list)
    
    # Error
    error_message: str = ""
    
    # Duration
    duration_seconds: float = 0.0
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionLog:
    """Лог выполнения"""
    log_id: str
    
    # References
    execution_id: str = ""
    step_id: str = ""
    
    # Level
    level: str = "info"  # debug, info, warning, error
    
    # Message
    message: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IntegrationHook:
    """Хук интеграции"""
    hook_id: str
    
    # Info
    name: str = ""
    description: str = ""
    
    # Type
    hook_type: str = "webhook"  # webhook, slack, email, pagerduty
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Events
    events: List[str] = field(default_factory=list)
    
    # Status
    is_enabled: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RunbookMetrics:
    """Метрики runbook"""
    metrics_id: str
    
    # Runbooks
    total_runbooks: int = 0
    published_runbooks: int = 0
    
    # Executions
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    running_executions: int = 0
    
    # Performance
    avg_duration_seconds: float = 0.0
    
    # Success rate
    success_rate: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class RunbookAutomationPlatform:
    """Платформа автоматизации runbook'ов"""
    
    def __init__(self, platform_name: str = "runbook-automation"):
        self.platform_name = platform_name
        self.runbooks: Dict[str, Runbook] = {}
        self.executions: Dict[str, RunbookExecution] = {}
        self.step_executions: Dict[str, StepExecution] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.execution_logs: List[ExecutionLog] = []
        self.hooks: Dict[str, IntegrationHook] = {}
        
        # Step handlers
        self._step_handlers: Dict[StepType, Callable] = {}
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Регистрация обработчиков шагов по умолчанию"""
        async def command_handler(step: Step, context: Dict) -> StepOutput:
            await asyncio.sleep(0.05)
            return StepOutput(
                output_id=f"out_{uuid.uuid4().hex[:8]}",
                stdout=f"Executed: {step.content}",
                return_code=0
            )
            
        async def script_handler(step: Step, context: Dict) -> StepOutput:
            await asyncio.sleep(0.1)
            return StepOutput(
                output_id=f"out_{uuid.uuid4().hex[:8]}",
                stdout=f"Script executed successfully",
                return_code=0,
                data={"result": "success"}
            )
            
        async def api_call_handler(step: Step, context: Dict) -> StepOutput:
            await asyncio.sleep(0.03)
            return StepOutput(
                output_id=f"out_{uuid.uuid4().hex[:8]}",
                data={"status": 200, "response": "OK"}
            )
            
        async def notification_handler(step: Step, context: Dict) -> StepOutput:
            await asyncio.sleep(0.02)
            return StepOutput(
                output_id=f"out_{uuid.uuid4().hex[:8]}",
                data={"sent": True, "channel": step.config.get("channel", "default")}
            )
            
        async def delay_handler(step: Step, context: Dict) -> StepOutput:
            delay = step.config.get("delay_seconds", 1)
            await asyncio.sleep(min(delay, 0.1))  # Cap for demo
            return StepOutput(
                output_id=f"out_{uuid.uuid4().hex[:8]}",
                data={"delayed": delay}
            )
            
        self._step_handlers[StepType.COMMAND] = command_handler
        self._step_handlers[StepType.SCRIPT] = script_handler
        self._step_handlers[StepType.API_CALL] = api_call_handler
        self._step_handlers[StepType.NOTIFICATION] = notification_handler
        self._step_handlers[StepType.DELAY] = delay_handler
        
    async def create_runbook(self, name: str,
                            display_name: str = "",
                            description: str = "",
                            runbook_type: RunbookType = RunbookType.REMEDIATION,
                            author: str = "",
                            owner_team: str = "",
                            tags: List[str] = None) -> Runbook:
        """Создание runbook"""
        runbook = Runbook(
            runbook_id=f"rb_{uuid.uuid4().hex[:8]}",
            name=name,
            display_name=display_name or name,
            description=description,
            runbook_type=runbook_type,
            author=author,
            owner_team=owner_team,
            tags=tags or []
        )
        
        self.runbooks[runbook.runbook_id] = runbook
        return runbook
        
    async def add_parameter(self, runbook_id: str,
                           name: str,
                           param_type: ParameterType = ParameterType.STRING,
                           required: bool = False,
                           default_value: Any = None,
                           description: str = "",
                           is_sensitive: bool = False) -> Optional[Parameter]:
        """Добавление параметра"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return None
            
        param = Parameter(
            param_id=f"prm_{uuid.uuid4().hex[:8]}",
            name=name,
            display_name=name.replace("_", " ").title(),
            description=description,
            param_type=param_type,
            required=required,
            default_value=default_value,
            is_sensitive=is_sensitive
        )
        
        runbook.parameters.append(param)
        return param
        
    async def add_step(self, runbook_id: str,
                      name: str,
                      step_type: StepType = StepType.COMMAND,
                      content: str = "",
                      description: str = "",
                      config: Dict[str, Any] = None,
                      on_failure: str = "fail",
                      timeout_seconds: int = 300,
                      condition: str = "",
                      approvers: List[str] = None,
                      depends_on: List[str] = None) -> Optional[Step]:
        """Добавление шага"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return None
            
        step = Step(
            step_id=f"stp_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            step_type=step_type,
            order=len(runbook.steps),
            content=content,
            config=config or {},
            on_failure=on_failure,
            timeout_seconds=timeout_seconds,
            condition=condition,
            approvers=approvers or [],
            depends_on=depends_on or []
        )
        
        runbook.steps.append(step)
        return step
        
    async def publish_runbook(self, runbook_id: str) -> Optional[Runbook]:
        """Публикация runbook"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return None
            
        runbook.status = RunbookStatus.PUBLISHED
        runbook.published_at = datetime.now()
        runbook.updated_at = datetime.now()
        
        return runbook
        
    async def execute_runbook(self, runbook_id: str,
                             parameters: Dict[str, Any] = None,
                             triggered_by: str = "",
                             trigger_type: TriggerType = TriggerType.MANUAL,
                             context: Dict[str, Any] = None) -> RunbookExecution:
        """Запуск runbook"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            raise ValueError(f"Runbook {runbook_id} not found")
            
        # Validate parameters
        params = parameters or {}
        for param in runbook.parameters:
            if param.required and param.name not in params:
                if param.default_value is not None:
                    params[param.name] = param.default_value
                else:
                    raise ValueError(f"Required parameter {param.name} missing")
                    
        execution = RunbookExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            runbook_id=runbook_id,
            runbook_name=runbook.name,
            runbook_version=runbook.version,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            parameters=params,
            total_steps=len(runbook.steps),
            context=context or {}
        )
        
        self.executions[execution.execution_id] = execution
        
        # Execute runbook
        await self._execute_runbook_steps(execution, runbook)
        
        # Update stats
        runbook.execution_count += 1
        if execution.status == ExecutionStatus.SUCCESS:
            runbook.success_count += 1
        elif execution.status == ExecutionStatus.FAILED:
            runbook.failure_count += 1
            
        return execution
        
    async def _execute_runbook_steps(self, execution: RunbookExecution, runbook: Runbook):
        """Выполнение шагов runbook"""
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()
        
        try:
            for i, step in enumerate(runbook.steps):
                execution.current_step = i + 1
                
                # Check condition
                if step.condition:
                    if not self._evaluate_condition(step.condition, execution.variables):
                        await self._log(execution.execution_id, step.step_id, "info", f"Step {step.name} skipped (condition not met)")
                        continue
                        
                # Handle approval step
                if step.step_type == StepType.APPROVAL:
                    approval = await self._request_approval(execution.execution_id, step)
                    if approval.status != ApprovalStatus.APPROVED:
                        execution.status = ExecutionStatus.CANCELLED
                        execution.error_message = "Approval rejected"
                        break
                    continue
                    
                # Execute step
                step_exec = await self._execute_step(execution, step)
                execution.step_executions.append(step_exec)
                
                # Store output in variables
                if step.output_variable and step_exec.output:
                    execution.variables[step.output_variable] = step_exec.output.data
                    
                # Handle failure
                if step_exec.status == ExecutionStatus.FAILED:
                    if step.on_failure == "fail":
                        execution.status = ExecutionStatus.FAILED
                        execution.error_message = step_exec.error_message
                        break
                    elif step.on_failure == "skip":
                        await self._log(execution.execution_id, step.step_id, "warning", f"Step {step.name} failed, skipping")
                        continue
                    elif step.on_failure == "continue":
                        await self._log(execution.execution_id, step.step_id, "warning", f"Step {step.name} failed, continuing")
                        continue
                        
            if execution.status == ExecutionStatus.RUNNING:
                execution.status = ExecutionStatus.SUCCESS
                
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            
        execution.completed_at = datetime.now()
        execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
        
    async def _execute_step(self, execution: RunbookExecution, step: Step) -> StepExecution:
        """Выполнение одного шага"""
        step_exec = StepExecution(
            execution_id=f"se_{uuid.uuid4().hex[:8]}",
            runbook_execution_id=execution.execution_id,
            step_id=step.step_id,
            step_name=step.name,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.step_executions[step_exec.execution_id] = step_exec
        
        await self._log(execution.execution_id, step.step_id, "info", f"Starting step: {step.name}")
        
        try:
            handler = self._step_handlers.get(step.step_type)
            if handler:
                output = await handler(step, execution.variables)
                step_exec.output = output
                step_exec.status = ExecutionStatus.SUCCESS
            else:
                # Default: simulate execution
                await asyncio.sleep(0.05)
                step_exec.output = StepOutput(
                    output_id=f"out_{uuid.uuid4().hex[:8]}",
                    stdout="Step executed",
                    return_code=0
                )
                step_exec.status = ExecutionStatus.SUCCESS
                
            await self._log(execution.execution_id, step.step_id, "info", f"Step completed: {step.name}")
            
        except Exception as e:
            step_exec.status = ExecutionStatus.FAILED
            step_exec.error_message = str(e)
            await self._log(execution.execution_id, step.step_id, "error", f"Step failed: {str(e)}")
            
        step_exec.completed_at = datetime.now()
        step_exec.duration_seconds = (step_exec.completed_at - step_exec.started_at).total_seconds()
        
        return step_exec
        
    async def _request_approval(self, execution_id: str, step: Step) -> ApprovalRequest:
        """Запрос одобрения"""
        request = ApprovalRequest(
            request_id=f"apr_{uuid.uuid4().hex[:8]}",
            runbook_execution_id=execution_id,
            step_id=step.step_id,
            approvers=step.approvers,
            expires_at=datetime.now() + timedelta(minutes=step.approval_timeout_minutes)
        )
        
        # Auto-approve for demo
        request.status = ApprovalStatus.APPROVED
        request.approved_by = step.approvers[0] if step.approvers else "auto"
        request.resolved_at = datetime.now()
        
        self.approval_requests[request.request_id] = request
        
        return request
        
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Оценка условия"""
        # Simplified condition evaluation
        if not condition:
            return True
            
        # For demo, always return True
        return True
        
    async def _log(self, execution_id: str, step_id: str, level: str, message: str):
        """Запись в лог"""
        log = ExecutionLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            execution_id=execution_id,
            step_id=step_id,
            level=level,
            message=message
        )
        
        self.execution_logs.append(log)
        
    async def cancel_execution(self, execution_id: str) -> Optional[RunbookExecution]:
        """Отмена выполнения"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
            
        if execution.status == ExecutionStatus.RUNNING:
            execution.status = ExecutionStatus.CANCELLED
            execution.completed_at = datetime.now()
            
        return execution
        
    async def create_hook(self, name: str,
                         hook_type: str = "webhook",
                         config: Dict[str, Any] = None,
                         events: List[str] = None) -> IntegrationHook:
        """Создание хука интеграции"""
        hook = IntegrationHook(
            hook_id=f"hk_{uuid.uuid4().hex[:8]}",
            name=name,
            hook_type=hook_type,
            config=config or {},
            events=events or ["execution.started", "execution.completed", "execution.failed"]
        )
        
        self.hooks[hook.hook_id] = hook
        return hook
        
    async def collect_metrics(self) -> RunbookMetrics:
        """Сбор метрик"""
        published = sum(1 for r in self.runbooks.values() if r.status == RunbookStatus.PUBLISHED)
        successful = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED)
        running = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.RUNNING)
        
        # Calculate average duration
        durations = [e.duration_seconds for e in self.executions.values() if e.duration_seconds > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Success rate
        total_completed = successful + failed
        success_rate = (successful / total_completed * 100) if total_completed > 0 else 0.0
        
        return RunbookMetrics(
            metrics_id=f"rbm_{uuid.uuid4().hex[:8]}",
            total_runbooks=len(self.runbooks),
            published_runbooks=published,
            total_executions=len(self.executions),
            successful_executions=successful,
            failed_executions=failed,
            running_executions=running,
            avg_duration_seconds=avg_duration,
            success_rate=success_rate
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        published = sum(1 for r in self.runbooks.values() if r.status == RunbookStatus.PUBLISHED)
        successful = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED)
        running = sum(1 for e in self.executions.values() if e.status == ExecutionStatus.RUNNING)
        
        runbooks_by_type = {}
        for rb in self.runbooks.values():
            rb_type = rb.runbook_type.value
            runbooks_by_type[rb_type] = runbooks_by_type.get(rb_type, 0) + 1
            
        executions_by_trigger = {}
        for ex in self.executions.values():
            trigger = ex.trigger_type.value
            executions_by_trigger[trigger] = executions_by_trigger.get(trigger, 0) + 1
            
        return {
            "total_runbooks": len(self.runbooks),
            "published_runbooks": published,
            "runbooks_by_type": runbooks_by_type,
            "total_executions": len(self.executions),
            "successful_executions": successful,
            "failed_executions": failed,
            "running_executions": running,
            "executions_by_trigger": executions_by_trigger,
            "total_step_executions": len(self.step_executions),
            "approval_requests": len(self.approval_requests),
            "execution_logs": len(self.execution_logs),
            "integration_hooks": len(self.hooks)
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 363: Runbook Automation Platform")
    print("=" * 60)
    
    platform = RunbookAutomationPlatform(platform_name="enterprise-runbook")
    print("✓ Runbook Automation Platform initialized")
    
    # Create Runbooks
    print("\n📋 Creating Runbooks...")
    
    runbooks_data = [
        ("restart-service", "Restart Service", "Safely restart a service with health checks", RunbookType.MAINTENANCE, "SRE Team", ["service", "restart", "maintenance"]),
        ("scale-deployment", "Scale Deployment", "Scale Kubernetes deployment horizontally", RunbookType.REMEDIATION, "Platform Team", ["kubernetes", "scale", "deployment"]),
        ("database-failover", "Database Failover", "Perform database failover to replica", RunbookType.RECOVERY, "DBA Team", ["database", "failover", "recovery"]),
        ("ssl-certificate-renewal", "SSL Certificate Renewal", "Renew SSL certificates before expiry", RunbookType.MAINTENANCE, "Security Team", ["ssl", "certificate", "security"]),
        ("incident-response", "Incident Response", "Standard incident response procedure", RunbookType.INCIDENT, "SRE Team", ["incident", "response", "oncall"]),
        ("deploy-canary", "Canary Deployment", "Deploy new version using canary strategy", RunbookType.DEPLOYMENT, "DevOps Team", ["deployment", "canary", "release"]),
        ("diagnose-high-cpu", "Diagnose High CPU", "Diagnose and remediate high CPU usage", RunbookType.DIAGNOSTIC, "SRE Team", ["cpu", "diagnostic", "performance"]),
        ("backup-verification", "Backup Verification", "Verify backup integrity and restore capability", RunbookType.MAINTENANCE, "DBA Team", ["backup", "verification", "disaster-recovery"])
    ]
    
    runbooks = []
    for name, display, desc, rb_type, team, tags in runbooks_data:
        rb = await platform.create_runbook(name, display, desc, rb_type, "admin", team, tags)
        runbooks.append(rb)
        print(f"  📋 {display} ({rb_type.value})")
        
    # Add Parameters to Runbooks
    print("\n📝 Adding Parameters...")
    
    # Restart Service Parameters
    await platform.add_parameter(runbooks[0].runbook_id, "service_name", ParameterType.STRING, True, description="Service to restart")
    await platform.add_parameter(runbooks[0].runbook_id, "environment", ParameterType.STRING, True, "production", description="Target environment")
    await platform.add_parameter(runbooks[0].runbook_id, "wait_healthy", ParameterType.BOOLEAN, False, True, description="Wait for health check")
    
    # Scale Deployment Parameters
    await platform.add_parameter(runbooks[1].runbook_id, "deployment_name", ParameterType.STRING, True)
    await platform.add_parameter(runbooks[1].runbook_id, "namespace", ParameterType.STRING, True, "default")
    await platform.add_parameter(runbooks[1].runbook_id, "replicas", ParameterType.NUMBER, True, 3)
    
    # Database Failover Parameters
    await platform.add_parameter(runbooks[2].runbook_id, "database_cluster", ParameterType.STRING, True)
    await platform.add_parameter(runbooks[2].runbook_id, "target_replica", ParameterType.STRING, True)
    await platform.add_parameter(runbooks[2].runbook_id, "force", ParameterType.BOOLEAN, False, False)
    
    print(f"  📝 Added parameters to {len(runbooks)} runbooks")
    
    # Add Steps to Runbooks
    print("\n⚙️ Adding Steps...")
    
    # Restart Service Steps
    await platform.add_step(runbooks[0].runbook_id, "Check service status", StepType.COMMAND, "kubectl get pods -l app=${service_name}", on_failure="fail")
    await platform.add_step(runbooks[0].runbook_id, "Notify start", StepType.NOTIFICATION, config={"channel": "#ops", "message": "Starting restart"})
    await platform.add_step(runbooks[0].runbook_id, "Approval required", StepType.APPROVAL, approvers=["sre-lead", "oncall"])
    await platform.add_step(runbooks[0].runbook_id, "Scale down", StepType.COMMAND, "kubectl scale deployment ${service_name} --replicas=0", timeout_seconds=120)
    await platform.add_step(runbooks[0].runbook_id, "Wait 10 seconds", StepType.DELAY, config={"delay_seconds": 10})
    await platform.add_step(runbooks[0].runbook_id, "Scale up", StepType.COMMAND, "kubectl scale deployment ${service_name} --replicas=3", timeout_seconds=120)
    await platform.add_step(runbooks[0].runbook_id, "Health check", StepType.SCRIPT, "health_check.sh ${service_name}", on_failure="retry", timeout_seconds=300)
    await platform.add_step(runbooks[0].runbook_id, "Notify complete", StepType.NOTIFICATION, config={"channel": "#ops", "message": "Restart completed"})
    
    # Scale Deployment Steps
    await platform.add_step(runbooks[1].runbook_id, "Get current replicas", StepType.COMMAND, "kubectl get deployment ${deployment_name} -o jsonpath='{.spec.replicas}'")
    await platform.add_step(runbooks[1].runbook_id, "Scale deployment", StepType.COMMAND, "kubectl scale deployment ${deployment_name} --replicas=${replicas} -n ${namespace}")
    await platform.add_step(runbooks[1].runbook_id, "Wait for rollout", StepType.COMMAND, "kubectl rollout status deployment ${deployment_name} -n ${namespace}", timeout_seconds=600)
    await platform.add_step(runbooks[1].runbook_id, "Verify scaling", StepType.COMMAND, "kubectl get pods -l app=${deployment_name} -n ${namespace}")
    
    # Database Failover Steps
    await platform.add_step(runbooks[2].runbook_id, "Check replication lag", StepType.API_CALL, config={"endpoint": "/api/db/replication/lag"})
    await platform.add_step(runbooks[2].runbook_id, "Emergency approval", StepType.APPROVAL, approvers=["dba-lead", "sre-lead"])
    await platform.add_step(runbooks[2].runbook_id, "Stop writes to primary", StepType.COMMAND, "pg_ctl stop -m fast")
    await platform.add_step(runbooks[2].runbook_id, "Promote replica", StepType.COMMAND, "pg_ctl promote -D ${target_replica}")
    await platform.add_step(runbooks[2].runbook_id, "Update connection strings", StepType.SCRIPT, "update_db_config.sh ${target_replica}")
    await platform.add_step(runbooks[2].runbook_id, "Verify new primary", StepType.API_CALL, config={"endpoint": "/api/db/health"})
    
    # Incident Response Steps
    await platform.add_step(runbooks[4].runbook_id, "Create incident ticket", StepType.API_CALL, config={"endpoint": "/api/incidents/create"})
    await platform.add_step(runbooks[4].runbook_id, "Page on-call", StepType.NOTIFICATION, config={"channel": "pagerduty"})
    await platform.add_step(runbooks[4].runbook_id, "Gather metrics", StepType.SCRIPT, "gather_metrics.sh")
    await platform.add_step(runbooks[4].runbook_id, "Post to war room", StepType.NOTIFICATION, config={"channel": "#incidents"})
    
    print(f"  ⚙️ Added steps to runbooks")
    
    # Publish Runbooks
    print("\n📤 Publishing Runbooks...")
    
    for rb in runbooks[:6]:
        await platform.publish_runbook(rb.runbook_id)
        
    print(f"  📤 Published 6 runbooks")
    
    # Create Integration Hooks
    print("\n🔗 Creating Integration Hooks...")
    
    hooks_data = [
        ("slack-notifications", "slack", {"webhook_url": "https://hooks.slack.com/...", "channel": "#runbook-executions"}),
        ("pagerduty-alerts", "pagerduty", {"service_key": "abc123"}),
        ("webhook-audit", "webhook", {"url": "https://audit.example.com/runbook"}),
        ("email-summary", "email", {"recipients": ["ops@example.com"]})
    ]
    
    for name, hook_type, config in hooks_data:
        await platform.create_hook(name, hook_type, config)
        print(f"  🔗 {name} ({hook_type})")
        
    # Execute Runbooks
    print("\n🚀 Executing Runbooks...")
    
    executions_data = [
        (runbooks[0].runbook_id, {"service_name": "api-gateway", "environment": "production"}, "john.smith", TriggerType.MANUAL),
        (runbooks[1].runbook_id, {"deployment_name": "order-service", "namespace": "production", "replicas": 5}, "jane.doe", TriggerType.ALERT),
        (runbooks[0].runbook_id, {"service_name": "payment-service", "environment": "staging"}, "bob.wilson", TriggerType.MANUAL),
        (runbooks[4].runbook_id, {}, "oncall-bot", TriggerType.ALERT),
        (runbooks[1].runbook_id, {"deployment_name": "notification-service", "namespace": "production", "replicas": 3}, "system", TriggerType.SCHEDULED),
        (runbooks[0].runbook_id, {"service_name": "user-service", "environment": "production"}, "alice.brown", TriggerType.WEBHOOK)
    ]
    
    executions = []
    for rb_id, params, user, trigger in executions_data:
        execution = await platform.execute_runbook(rb_id, params, user, trigger)
        executions.append(execution)
        status_icon = "✓" if execution.status == ExecutionStatus.SUCCESS else "✗"
        print(f"  {status_icon} {execution.runbook_name}: {execution.status.value} ({execution.duration_seconds:.2f}s)")
        
    # Collect Metrics
    metrics = await platform.collect_metrics()
    
    # Runbooks Dashboard
    print("\n📋 Runbooks:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                         │ Type           │ Status      │ Steps  │ Executions │ Success Rate                                                                                                                                                                                                                                                                                                                                                                                                                    │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for rb in runbooks:
        name = rb.display_name[:28].ljust(28)
        rb_type = rb.runbook_type.value[:14].ljust(14)
        status = rb.status.value[:11].ljust(11)
        steps = str(len(rb.steps)).ljust(6)
        exec_count = str(rb.execution_count).ljust(10)
        success_rate = f"{(rb.success_count/rb.execution_count*100):.0f}%" if rb.execution_count > 0 else "N/A"
        success_rate = success_rate.ljust(100)
        
        print(f"  │ {name} │ {rb_type} │ {status} │ {steps} │ {exec_count} │ {success_rate} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Executions Dashboard
    print("\n🚀 Recent Executions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ ID             │ Runbook                      │ Trigger     │ Status      │ Steps      │ Duration   │ User                                                                                                                                                                                                                                                                                                                                                                                                               │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ex in executions:
        ex_id = ex.execution_id[:14].ljust(14)
        rb_name = ex.runbook_name[:28].ljust(28)
        trigger = ex.trigger_type.value[:11].ljust(11)
        status = ex.status.value[:11].ljust(11)
        steps = f"{ex.current_step}/{ex.total_steps}".ljust(10)
        duration = f"{ex.duration_seconds:.2f}s".ljust(10)
        user = ex.triggered_by[:80] if ex.triggered_by else "system"
        user = user.ljust(80)
        
        print(f"  │ {ex_id} │ {rb_name} │ {trigger} │ {status} │ {steps} │ {duration} │ {user} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Step Executions for First Execution
    print("\n⚙️ Step Executions (First Runbook):")
    
    first_exec = executions[0]
    for step_exec in first_exec.step_executions:
        status_icon = "✓" if step_exec.status == ExecutionStatus.SUCCESS else "✗"
        print(f"  {status_icon} {step_exec.step_name}: {step_exec.status.value} ({step_exec.duration_seconds:.3f}s)")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Total Runbooks: {stats['total_runbooks']} ({stats['published_runbooks']} published)")
    print(f"  Total Executions: {stats['total_executions']}")
    print(f"  Successful: {stats['successful_executions']}")
    print(f"  Failed: {stats['failed_executions']}")
    print(f"  Success Rate: {metrics.success_rate:.1f}%")
    print(f"  Avg Duration: {metrics.avg_duration_seconds:.2f}s")
    
    # Runbooks by Type
    print("\n  Runbooks by Type:")
    for rb_type, count in stats["runbooks_by_type"].items():
        bar = "█" * count
        print(f"    {rb_type:15s} │ {bar} ({count})")
        
    # Executions by Trigger
    print("\n  Executions by Trigger:")
    for trigger, count in stats["executions_by_trigger"].items():
        bar = "█" * count
        print(f"    {trigger:12s} │ {bar} ({count})")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Runbook Automation Platform                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Runbooks:                {stats['total_runbooks']:>12}                      │")
    print(f"│ Published Runbooks:            {stats['published_runbooks']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Executions:              {stats['total_executions']:>12}                      │")
    print(f"│ Successful:                    {stats['successful_executions']:>12}                      │")
    print(f"│ Failed:                        {stats['failed_executions']:>12}                      │")
    print(f"│ Success Rate:                  {metrics.success_rate:>11.1f}%                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Step Executions:               {stats['total_step_executions']:>12}                      │")
    print(f"│ Approval Requests:             {stats['approval_requests']:>12}                      │")
    print(f"│ Avg Duration (s):              {metrics.avg_duration_seconds:>12.2f}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Execution Logs:                {stats['execution_logs']:>12}                      │")
    print(f"│ Integration Hooks:             {stats['integration_hooks']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Runbook Automation Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
