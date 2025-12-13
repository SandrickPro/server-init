#!/usr/bin/env python3
"""
Server Init - Iteration 107: Runbook Automation Platform
Платформа автоматизации ранбуков

Функционал:
- Runbook Management - управление ранбуками
- Step Execution - выполнение шагов
- Conditional Logic - условная логика
- Approval Workflows - согласования
- Parameterization - параметризация
- Execution History - история выполнения
- Integration - интеграции
- Scheduling - планирование
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum
from collections import defaultdict
import uuid
import random


class StepType(Enum):
    """Тип шага"""
    SCRIPT = "script"
    COMMAND = "command"
    API_CALL = "api_call"
    MANUAL = "manual"
    APPROVAL = "approval"
    CONDITION = "condition"
    PARALLEL = "parallel"
    WAIT = "wait"
    NOTIFICATION = "notification"


class ExecutionStatus(Enum):
    """Статус выполнения"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    ALERT = "alert"
    EVENT = "event"


@dataclass
class Parameter:
    """Параметр"""
    name: str
    param_type: str = "string"  # string, number, boolean, secret
    description: str = ""
    required: bool = True
    default: Any = None
    allowed_values: List[Any] = field(default_factory=list)


@dataclass
class Step:
    """Шаг ранбука"""
    step_id: str
    name: str = ""
    
    # Type
    step_type: StepType = StepType.COMMAND
    
    # Execution
    command: str = ""
    script: str = ""
    api_endpoint: str = ""
    
    # Timeout
    timeout_seconds: int = 300
    
    # Retry
    retry_count: int = 0
    retry_delay_seconds: int = 30
    
    # Conditions
    condition: str = ""  # Expression to evaluate
    on_failure: str = "stop"  # stop, continue, skip
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Outputs
    outputs: Dict[str, str] = field(default_factory=dict)


@dataclass
class Runbook:
    """Ранбук"""
    runbook_id: str
    
    # Basic info
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Category
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: List[Parameter] = field(default_factory=list)
    
    # Steps
    steps: List[Step] = field(default_factory=list)
    
    # Approval
    requires_approval: bool = False
    approvers: List[str] = field(default_factory=list)
    
    # Triggers
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Settings
    enabled: bool = True
    timeout_seconds: int = 3600
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Owner
    owner: str = ""


@dataclass
class StepExecution:
    """Выполнение шага"""
    step_id: str
    step_name: str = ""
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Times
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Output
    output: str = ""
    error: str = ""
    
    # Retries
    attempt: int = 1
    
    # Variables
    outputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunbookExecution:
    """Выполнение ранбука"""
    execution_id: str
    runbook_id: str
    runbook_name: str = ""
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    triggered_by: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Steps
    step_executions: Dict[str, StepExecution] = field(default_factory=dict)
    current_step: Optional[str] = None
    
    # Approval
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None
    
    # Times
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    
    # Logs
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScheduledTrigger:
    """Запланированный триггер"""
    trigger_id: str
    runbook_id: str
    
    # Schedule
    cron_expression: str = ""
    timezone: str = "UTC"
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class StepExecutor:
    """Исполнитель шагов"""
    
    async def execute(self, step: Step, context: Dict[str, Any]) -> StepExecution:
        """Выполнение шага"""
        execution = StepExecution(
            step_id=step.step_id,
            step_name=step.name,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            if step.step_type == StepType.COMMAND:
                execution = await self._execute_command(step, execution, context)
            elif step.step_type == StepType.SCRIPT:
                execution = await self._execute_script(step, execution, context)
            elif step.step_type == StepType.API_CALL:
                execution = await self._execute_api_call(step, execution, context)
            elif step.step_type == StepType.WAIT:
                execution = await self._execute_wait(step, execution, context)
            elif step.step_type == StepType.NOTIFICATION:
                execution = await self._execute_notification(step, execution, context)
            elif step.step_type == StepType.MANUAL:
                execution.status = ExecutionStatus.WAITING_APPROVAL
                execution.output = "Waiting for manual confirmation"
            elif step.step_type == StepType.APPROVAL:
                execution.status = ExecutionStatus.WAITING_APPROVAL
                execution.output = "Waiting for approval"
            else:
                execution.status = ExecutionStatus.SUCCEEDED
                
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            
        execution.finished_at = datetime.now()
        return execution
        
    async def _execute_command(self, step: Step, execution: StepExecution,
                                context: Dict[str, Any]) -> StepExecution:
        """Выполнение команды"""
        # Simulate command execution
        await asyncio.sleep(0.1)
        
        if random.random() > 0.1:  # 90% success
            execution.status = ExecutionStatus.SUCCEEDED
            execution.output = f"Command '{step.command}' executed successfully"
            execution.outputs["exit_code"] = 0
        else:
            execution.status = ExecutionStatus.FAILED
            execution.error = "Command failed with exit code 1"
            execution.outputs["exit_code"] = 1
            
        return execution
        
    async def _execute_script(self, step: Step, execution: StepExecution,
                               context: Dict[str, Any]) -> StepExecution:
        """Выполнение скрипта"""
        await asyncio.sleep(0.2)
        
        execution.status = ExecutionStatus.SUCCEEDED
        execution.output = "Script executed"
        return execution
        
    async def _execute_api_call(self, step: Step, execution: StepExecution,
                                 context: Dict[str, Any]) -> StepExecution:
        """Выполнение API вызова"""
        await asyncio.sleep(0.1)
        
        execution.status = ExecutionStatus.SUCCEEDED
        execution.output = json.dumps({"status": "ok", "data": {}})
        execution.outputs["response_code"] = 200
        return execution
        
    async def _execute_wait(self, step: Step, execution: StepExecution,
                             context: Dict[str, Any]) -> StepExecution:
        """Ожидание"""
        wait_seconds = int(step.command) if step.command.isdigit() else 1
        await asyncio.sleep(min(wait_seconds, 1))  # Limit for demo
        
        execution.status = ExecutionStatus.SUCCEEDED
        execution.output = f"Waited {wait_seconds} seconds"
        return execution
        
    async def _execute_notification(self, step: Step, execution: StepExecution,
                                     context: Dict[str, Any]) -> StepExecution:
        """Отправка уведомления"""
        execution.status = ExecutionStatus.SUCCEEDED
        execution.output = f"Notification sent: {step.command}"
        return execution


class RunbookEngine:
    """Движок ранбуков"""
    
    def __init__(self):
        self.step_executor = StepExecutor()
        
    async def execute(self, runbook: Runbook,
                       parameters: Dict[str, Any],
                       triggered_by: str,
                       trigger_type: TriggerType = TriggerType.MANUAL) -> RunbookExecution:
        """Выполнение ранбука"""
        execution = RunbookExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            runbook_id=runbook.runbook_id,
            runbook_name=runbook.name,
            status=ExecutionStatus.RUNNING,
            trigger_type=trigger_type,
            triggered_by=triggered_by,
            parameters=parameters
        )
        
        # Log start
        execution.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": "info",
            "message": f"Started execution of runbook '{runbook.name}'"
        })
        
        # Check approval if required
        if runbook.requires_approval:
            execution.status = ExecutionStatus.WAITING_APPROVAL
            execution.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "info",
                "message": "Waiting for approval"
            })
            return execution
            
        # Build context
        context = {
            "parameters": parameters,
            "execution_id": execution.execution_id,
            "outputs": {}
        }
        
        # Execute steps
        for step in runbook.steps:
            execution.current_step = step.step_id
            
            # Check condition
            if step.condition:
                # Simulate condition evaluation
                if not self._evaluate_condition(step.condition, context):
                    step_exec = StepExecution(
                        step_id=step.step_id,
                        step_name=step.name,
                        status=ExecutionStatus.SKIPPED,
                        output="Condition not met"
                    )
                    execution.step_executions[step.step_id] = step_exec
                    continue
                    
            # Execute step
            step_exec = await self.step_executor.execute(step, context)
            execution.step_executions[step.step_id] = step_exec
            
            # Log step result
            execution.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "info" if step_exec.status == ExecutionStatus.SUCCEEDED else "error",
                "message": f"Step '{step.name}': {step_exec.status.value}"
            })
            
            # Update context with outputs
            context["outputs"][step.step_id] = step_exec.outputs
            
            # Handle failure
            if step_exec.status == ExecutionStatus.FAILED:
                if step.on_failure == "stop":
                    execution.status = ExecutionStatus.FAILED
                    break
                elif step.on_failure == "skip":
                    continue
                    
            # Handle waiting states
            if step_exec.status == ExecutionStatus.WAITING_APPROVAL:
                execution.status = ExecutionStatus.WAITING_APPROVAL
                return execution
                
        # Determine final status
        if execution.status != ExecutionStatus.FAILED:
            failed_steps = [s for s in execution.step_executions.values() 
                           if s.status == ExecutionStatus.FAILED]
            if failed_steps:
                execution.status = ExecutionStatus.FAILED
            else:
                execution.status = ExecutionStatus.SUCCEEDED
                
        execution.finished_at = datetime.now()
        execution.current_step = None
        
        return execution
        
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Оценка условия"""
        # Simplified condition evaluation
        return random.random() > 0.3


class RunbookManager:
    """Менеджер ранбуков"""
    
    def __init__(self):
        self.runbooks: Dict[str, Runbook] = {}
        self.engine = RunbookEngine()
        self.executions: Dict[str, RunbookExecution] = {}
        self.scheduled_triggers: Dict[str, ScheduledTrigger] = {}
        
    def create(self, name: str, description: str = "",
                category: str = "", **kwargs) -> Runbook:
        """Создание ранбука"""
        runbook = Runbook(
            runbook_id=f"rb_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            category=category,
            **kwargs
        )
        self.runbooks[runbook.runbook_id] = runbook
        return runbook
        
    def add_step(self, runbook_id: str, name: str,
                  step_type: StepType, **kwargs) -> Optional[Step]:
        """Добавление шага"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return None
            
        step = Step(
            step_id=f"step_{uuid.uuid4().hex[:8]}",
            name=name,
            step_type=step_type,
            **kwargs
        )
        runbook.steps.append(step)
        return step
        
    def add_parameter(self, runbook_id: str, name: str,
                       param_type: str = "string", **kwargs) -> bool:
        """Добавление параметра"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            return False
            
        param = Parameter(name=name, param_type=param_type, **kwargs)
        runbook.parameters.append(param)
        return True
        
    async def execute(self, runbook_id: str, parameters: Dict[str, Any],
                       triggered_by: str,
                       trigger_type: TriggerType = TriggerType.MANUAL) -> RunbookExecution:
        """Выполнение"""
        runbook = self.runbooks.get(runbook_id)
        if not runbook:
            exec = RunbookExecution(
                execution_id=f"exec_{uuid.uuid4().hex[:8]}",
                runbook_id=runbook_id,
                status=ExecutionStatus.FAILED
            )
            exec.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "error",
                "message": "Runbook not found"
            })
            return exec
            
        execution = await self.engine.execute(
            runbook, parameters, triggered_by, trigger_type
        )
        self.executions[execution.execution_id] = execution
        return execution
        
    def approve(self, execution_id: str, approver: str) -> bool:
        """Одобрение"""
        execution = self.executions.get(execution_id)
        if execution and execution.status == ExecutionStatus.WAITING_APPROVAL:
            execution.approval_status = "approved"
            execution.approved_by = approver
            execution.status = ExecutionStatus.APPROVED
            return True
        return False
        
    def reject(self, execution_id: str, rejector: str, reason: str = "") -> bool:
        """Отклонение"""
        execution = self.executions.get(execution_id)
        if execution and execution.status == ExecutionStatus.WAITING_APPROVAL:
            execution.approval_status = "rejected"
            execution.status = ExecutionStatus.REJECTED
            execution.logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "warning",
                "message": f"Rejected by {rejector}: {reason}"
            })
            return True
        return False
        
    def schedule(self, runbook_id: str, cron_expression: str,
                  parameters: Dict[str, Any] = None) -> ScheduledTrigger:
        """Планирование"""
        trigger = ScheduledTrigger(
            trigger_id=f"trig_{uuid.uuid4().hex[:8]}",
            runbook_id=runbook_id,
            cron_expression=cron_expression,
            parameters=parameters or {},
            next_run=datetime.now() + timedelta(hours=1)
        )
        self.scheduled_triggers[trigger.trigger_id] = trigger
        return trigger


class RunbookAutomationPlatform:
    """Платформа автоматизации ранбуков"""
    
    def __init__(self):
        self.manager = RunbookManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        executions = list(self.manager.executions.values())
        
        status_counts = defaultdict(int)
        for exec in executions:
            status_counts[exec.status.value] += 1
            
        total_steps = sum(
            len(rb.steps) for rb in self.manager.runbooks.values()
        )
        
        # Calculate success rate
        completed = [e for e in executions 
                     if e.status in [ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED]]
        success_rate = (
            len([e for e in completed if e.status == ExecutionStatus.SUCCEEDED]) 
            / len(completed) * 100
        ) if completed else 0
        
        return {
            "runbooks": len(self.manager.runbooks),
            "total_steps": total_steps,
            "executions": len(executions),
            "status_counts": dict(status_counts),
            "success_rate": success_rate,
            "scheduled_triggers": len(self.manager.scheduled_triggers),
            "waiting_approval": status_counts.get("waiting_approval", 0)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 107: Runbook Automation Platform")
    print("=" * 60)
    
    async def demo():
        platform = RunbookAutomationPlatform()
        print("✓ Runbook Automation Platform created")
        
        # Create runbooks
        print("\n📚 Creating Runbooks...")
        
        # Runbook 1: Service restart
        rb1 = platform.manager.create(
            name="Service Restart",
            description="Restart a service with health checks",
            category="operations",
            tags=["restart", "service", "health-check"]
        )
        
        platform.manager.add_parameter(rb1.runbook_id, "service_name", "string",
                                        description="Name of the service to restart",
                                        required=True)
        platform.manager.add_parameter(rb1.runbook_id, "environment", "string",
                                        description="Target environment",
                                        allowed_values=["dev", "staging", "prod"])
        
        platform.manager.add_step(rb1.runbook_id, "Check service status",
                                   StepType.COMMAND, command="systemctl status {{service_name}}")
        platform.manager.add_step(rb1.runbook_id, "Stop service",
                                   StepType.COMMAND, command="systemctl stop {{service_name}}")
        platform.manager.add_step(rb1.runbook_id, "Wait for graceful shutdown",
                                   StepType.WAIT, command="10")
        platform.manager.add_step(rb1.runbook_id, "Start service",
                                   StepType.COMMAND, command="systemctl start {{service_name}}")
        platform.manager.add_step(rb1.runbook_id, "Verify health",
                                   StepType.API_CALL, api_endpoint="http://{{service_name}}/health")
        platform.manager.add_step(rb1.runbook_id, "Send notification",
                                   StepType.NOTIFICATION, command="Service {{service_name}} restarted")
        
        print(f"  ✓ {rb1.name} ({len(rb1.steps)} steps)")
        
        # Runbook 2: Database backup
        rb2 = platform.manager.create(
            name="Database Backup",
            description="Perform database backup with verification",
            category="database",
            requires_approval=True,
            approvers=["dba-team"]
        )
        
        platform.manager.add_parameter(rb2.runbook_id, "database", "string")
        platform.manager.add_parameter(rb2.runbook_id, "retention_days", "number", default=30)
        
        platform.manager.add_step(rb2.runbook_id, "Request approval",
                                   StepType.APPROVAL)
        platform.manager.add_step(rb2.runbook_id, "Create snapshot",
                                   StepType.SCRIPT, script="backup_database.sh")
        platform.manager.add_step(rb2.runbook_id, "Verify backup integrity",
                                   StepType.COMMAND, command="verify_backup.sh")
        platform.manager.add_step(rb2.runbook_id, "Upload to S3",
                                   StepType.COMMAND, command="aws s3 cp backup.sql s3://backups/")
        platform.manager.add_step(rb2.runbook_id, "Cleanup old backups",
                                   StepType.COMMAND, command="cleanup_old_backups.sh")
        
        print(f"  ✓ {rb2.name} ({len(rb2.steps)} steps, requires approval)")
        
        # Runbook 3: Incident response
        rb3 = platform.manager.create(
            name="Incident Response",
            description="Automated incident response procedures",
            category="incident"
        )
        
        platform.manager.add_parameter(rb3.runbook_id, "incident_id", "string")
        platform.manager.add_parameter(rb3.runbook_id, "severity", "string",
                                        allowed_values=["sev1", "sev2", "sev3"])
        
        platform.manager.add_step(rb3.runbook_id, "Collect logs",
                                   StepType.COMMAND, command="collect_logs.sh",
                                   on_failure="continue")
        platform.manager.add_step(rb3.runbook_id, "Capture metrics",
                                   StepType.API_CALL, api_endpoint="/api/metrics/snapshot")
        platform.manager.add_step(rb3.runbook_id, "Page on-call",
                                   StepType.NOTIFICATION, command="Incident {{incident_id}} detected")
        platform.manager.add_step(rb3.runbook_id, "Create war room",
                                   StepType.API_CALL, api_endpoint="/api/warroom/create")
        platform.manager.add_step(rb3.runbook_id, "Manual investigation",
                                   StepType.MANUAL)
        
        print(f"  ✓ {rb3.name} ({len(rb3.steps)} steps)")
        
        # Runbook 4: Scaling
        rb4 = platform.manager.create(
            name="Horizontal Scale",
            description="Scale service horizontally",
            category="scaling"
        )
        
        platform.manager.add_parameter(rb4.runbook_id, "service", "string")
        platform.manager.add_parameter(rb4.runbook_id, "replicas", "number")
        
        platform.manager.add_step(rb4.runbook_id, "Validate parameters",
                                   StepType.CONDITION, condition="replicas > 0 && replicas <= 10")
        platform.manager.add_step(rb4.runbook_id, "Scale deployment",
                                   StepType.COMMAND, command="kubectl scale --replicas={{replicas}}")
        platform.manager.add_step(rb4.runbook_id, "Wait for rollout",
                                   StepType.COMMAND, command="kubectl rollout status")
        platform.manager.add_step(rb4.runbook_id, "Verify health",
                                   StepType.API_CALL, api_endpoint="/health")
        
        print(f"  ✓ {rb4.name} ({len(rb4.steps)} steps)")
        
        # Execute runbooks
        print("\n⚡ Executing Runbooks...")
        
        # Execute service restart
        print(f"\n  Running: {rb1.name}")
        exec1 = await platform.manager.execute(
            rb1.runbook_id,
            {"service_name": "api-gateway", "environment": "staging"},
            "admin@company.com"
        )
        
        status_icon = "✓" if exec1.status == ExecutionStatus.SUCCEEDED else "✗"
        print(f"    {status_icon} Status: {exec1.status.value}")
        print(f"    Steps executed: {len(exec1.step_executions)}")
        
        for step_id, step_exec in exec1.step_executions.items():
            step_icon = {
                "succeeded": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "waiting_approval": "⏳"
            }.get(step_exec.status.value, "⚪")
            print(f"      {step_icon} {step_exec.step_name}: {step_exec.status.value}")
            
        # Execute with approval
        print(f"\n  Running: {rb2.name}")
        exec2 = await platform.manager.execute(
            rb2.runbook_id,
            {"database": "production-db", "retention_days": 30},
            "ops@company.com"
        )
        
        print(f"    ⏳ Status: {exec2.status.value}")
        
        # Approve
        print("    → Approving...")
        platform.manager.approve(exec2.execution_id, "dba@company.com")
        print(f"    ✓ Approved by dba@company.com")
        
        # Execute incident response
        print(f"\n  Running: {rb3.name}")
        exec3 = await platform.manager.execute(
            rb3.runbook_id,
            {"incident_id": "INC-001", "severity": "sev2"},
            "alertmanager",
            TriggerType.ALERT
        )
        
        print(f"    Status: {exec3.status.value}")
        
        # Schedule runbook
        print("\n📅 Scheduling Runbooks...")
        
        trigger1 = platform.manager.schedule(
            rb2.runbook_id,
            "0 2 * * *",  # Daily at 2 AM
            {"database": "production-db", "retention_days": 7}
        )
        print(f"  ✓ {rb2.name}: Daily at 2:00 AM")
        
        trigger2 = platform.manager.schedule(
            rb4.runbook_id,
            "0 8 * * 1-5",  # Weekdays at 8 AM
            {"service": "web-app", "replicas": 5}
        )
        print(f"  ✓ {rb4.name}: Weekdays at 8:00 AM")
        
        # Execution history
        print("\n📜 Execution History:")
        
        for exec_id, execution in platform.manager.executions.items():
            status_icon = {
                "succeeded": "✅",
                "failed": "❌",
                "waiting_approval": "⏳",
                "running": "🔄"
            }.get(execution.status.value, "⚪")
            
            duration = ""
            if execution.finished_at:
                dur = (execution.finished_at - execution.started_at).total_seconds()
                duration = f" ({dur:.1f}s)"
                
            print(f"  {status_icon} {execution.runbook_name} [{execution.trigger_type.value}]{duration}")
            
        # Logs sample
        print("\n📋 Recent Logs (Service Restart):")
        
        for log in exec1.logs[-5:]:
            level_icon = {"info": "ℹ️", "error": "❌", "warning": "⚠️"}.get(log["level"], "•")
            print(f"  {level_icon} {log['message']}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Runbooks: {stats['runbooks']}")
        print(f"  Total Steps: {stats['total_steps']}")
        print(f"  Executions: {stats['executions']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Scheduled Triggers: {stats['scheduled_triggers']}")
        print(f"  Waiting Approval: {stats['waiting_approval']}")
        
        print("\n  Execution Status:")
        for status, count in stats['status_counts'].items():
            icon = {
                "succeeded": "✅",
                "failed": "❌",
                "waiting_approval": "⏳",
                "running": "🔄"
            }.get(status, "⚪")
            print(f"    {icon} {status}: {count}")
            
        # Dashboard
        print("\n📋 Runbook Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Runbook Automation Overview                    │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Runbooks:           {stats['runbooks']:>10}                        │")
        print(f"  │ Total Steps:        {stats['total_steps']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Executions:         {stats['executions']:>10}                        │")
        print(f"  │ Success Rate:       {stats['success_rate']:>10.1f}%                       │")
        print(f"  │ Waiting Approval:   {stats['waiting_approval']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Scheduled:          {stats['scheduled_triggers']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Runbook Automation Platform initialized!")
    print("=" * 60)
