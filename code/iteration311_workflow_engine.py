#!/usr/bin/env python3
"""
Server Init - Iteration 311: Workflow Engine Platform
Платформа оркестрации рабочих процессов

Функционал:
- Workflow Definition - определение workflow
- Task Management - управление задачами
- Conditional Logic - условная логика
- Parallel Execution - параллельное выполнение
- Triggers - триггеры запуска
- State Machine - машина состояний
- Monitoring - мониторинг выполнения
- Retry & Error Handling - повторы и обработка ошибок
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class WorkflowStatus(Enum):
    """Статус workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(Enum):
    """Статус выполнения"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class TaskType(Enum):
    """Тип задачи"""
    ACTION = "action"
    DECISION = "decision"
    PARALLEL = "parallel"
    WAIT = "wait"
    NOTIFICATION = "notification"
    HTTP_REQUEST = "http_request"
    SCRIPT = "script"
    APPROVAL = "approval"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    EVENT = "event"


class RetryStrategy(Enum):
    """Стратегия повторов"""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"


@dataclass
class Task:
    """Задача workflow"""
    task_id: str
    name: str
    task_type: TaskType
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"script": "...", "params": {...}}
    
    # Flow
    next_tasks: List[str] = field(default_factory=list)  # task_ids
    condition: str = ""  # Expression for decision
    
    # Timeout
    timeout_seconds: int = 300
    
    # Retry
    retry_strategy: RetryStrategy = RetryStrategy.NONE
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Position (for visualization)
    x: int = 0
    y: int = 0


@dataclass
class Workflow:
    """Workflow"""
    workflow_id: str
    name: str
    description: str
    
    # Tasks
    tasks: Dict[str, Task] = field(default_factory=dict)
    start_task_id: str = ""
    
    # Status
    status: WorkflowStatus = WorkflowStatus.DRAFT
    
    # Version
    version: int = 1
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    
    # Variables
    input_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Organization
    owner_id: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Stats
    execution_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TaskExecution:
    """Выполнение задачи"""
    execution_id: str
    task_id: str
    workflow_execution_id: str
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Input/Output
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error
    error_message: str = ""
    
    # Retries
    retry_count: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0


@dataclass
class WorkflowExecution:
    """Выполнение workflow"""
    execution_id: str
    workflow_id: str
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    
    # Data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Task executions
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    current_task_id: str = ""
    
    # Error
    error_message: str = ""
    
    # Trigger
    triggered_by: str = ""  # user_id, "scheduler", "webhook"
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Trigger:
    """Триггер workflow"""
    trigger_id: str
    workflow_id: str
    
    # Type
    trigger_type: TriggerType = TriggerType.MANUAL
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    # Schedule: {"cron": "0 9 * * *"}
    # Webhook: {"secret": "..."}
    # Event: {"event_type": "...", "filters": {...}}
    
    # Status
    is_active: bool = True
    
    # Stats
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None


class WorkflowEngine:
    """Движок workflow"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.triggers: Dict[str, Trigger] = {}
        self.task_handlers: Dict[TaskType, Callable] = {}
        
        # Register default handlers
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """Регистрация обработчиков по умолчанию"""
        self.task_handlers[TaskType.ACTION] = self._handle_action
        self.task_handlers[TaskType.DECISION] = self._handle_decision
        self.task_handlers[TaskType.PARALLEL] = self._handle_parallel
        self.task_handlers[TaskType.WAIT] = self._handle_wait
        self.task_handlers[TaskType.NOTIFICATION] = self._handle_notification
        self.task_handlers[TaskType.HTTP_REQUEST] = self._handle_http
        self.task_handlers[TaskType.SCRIPT] = self._handle_script
        self.task_handlers[TaskType.APPROVAL] = self._handle_approval
        
    async def create_workflow(self, name: str,
                             description: str = "",
                             owner_id: str = "",
                             trigger_type: TriggerType = TriggerType.MANUAL) -> Workflow:
        """Создание workflow"""
        workflow = Workflow(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            owner_id=owner_id,
            trigger_type=trigger_type
        )
        
        self.workflows[workflow.workflow_id] = workflow
        return workflow
        
    async def add_task(self, workflow_id: str,
                      name: str,
                      task_type: TaskType,
                      config: Dict[str, Any] = None,
                      next_tasks: List[str] = None,
                      condition: str = "") -> Optional[Task]:
        """Добавление задачи"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            task_type=task_type,
            config=config or {},
            next_tasks=next_tasks or [],
            condition=condition
        )
        
        workflow.tasks[task.task_id] = task
        workflow.updated_at = datetime.now()
        
        # Set as start task if first task
        if not workflow.start_task_id:
            workflow.start_task_id = task.task_id
            
        return task
        
    async def set_start_task(self, workflow_id: str, task_id: str) -> bool:
        """Установка начальной задачи"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or task_id not in workflow.tasks:
            return False
            
        workflow.start_task_id = task_id
        return True
        
    async def connect_tasks(self, workflow_id: str,
                           from_task_id: str,
                           to_task_id: str) -> bool:
        """Соединение задач"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
            
        from_task = workflow.tasks.get(from_task_id)
        if not from_task or to_task_id not in workflow.tasks:
            return False
            
        if to_task_id not in from_task.next_tasks:
            from_task.next_tasks.append(to_task_id)
            
        return True
        
    async def activate_workflow(self, workflow_id: str) -> bool:
        """Активация workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
            
        workflow.status = WorkflowStatus.ACTIVE
        return True
        
    async def execute_workflow(self, workflow_id: str,
                              input_data: Dict[str, Any] = None,
                              triggered_by: str = "manual") -> Optional[WorkflowExecution]:
        """Запуск выполнения workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.ACTIVE:
            return None
            
        execution = WorkflowExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            input_data=input_data or {},
            context=dict(input_data or {}),
            triggered_by=triggered_by,
            current_task_id=workflow.start_task_id
        )
        
        self.executions[execution.execution_id] = execution
        workflow.execution_count += 1
        
        # Start execution
        await self._run_execution(execution.execution_id)
        
        return execution
        
    async def _run_execution(self, execution_id: str):
        """Запуск выполнения"""
        execution = self.executions.get(execution_id)
        if not execution:
            return
            
        workflow = self.workflows.get(execution.workflow_id)
        if not workflow:
            return
            
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()
        
        try:
            # Run tasks
            await self._run_task(execution_id, execution.current_task_id)
            
            # Check if completed
            if execution.status == ExecutionStatus.RUNNING:
                execution.status = ExecutionStatus.COMPLETED
                execution.output_data = execution.context
                
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            
        execution.completed_at = datetime.now()
        execution.duration_seconds = (
            execution.completed_at - execution.started_at
        ).total_seconds()
        
    async def _run_task(self, execution_id: str, task_id: str):
        """Выполнение задачи"""
        execution = self.executions.get(execution_id)
        if not execution:
            return
            
        workflow = self.workflows.get(execution.workflow_id)
        if not workflow:
            return
            
        task = workflow.tasks.get(task_id)
        if not task:
            return
            
        # Create task execution
        task_exec = TaskExecution(
            execution_id=f"texec_{uuid.uuid4().hex[:8]}",
            task_id=task_id,
            workflow_execution_id=execution_id,
            input_data=dict(execution.context)
        )
        
        execution.task_executions[task_id] = task_exec
        execution.current_task_id = task_id
        task_exec.status = ExecutionStatus.RUNNING
        task_exec.started_at = datetime.now()
        
        try:
            # Get handler
            handler = self.task_handlers.get(task.task_type)
            if handler:
                output = await handler(task, task_exec.input_data)
                task_exec.output_data = output
                execution.context.update(output)
                
            task_exec.status = ExecutionStatus.COMPLETED
            
        except Exception as e:
            task_exec.status = ExecutionStatus.FAILED
            task_exec.error_message = str(e)
            
            # Retry logic
            if (task.retry_strategy != RetryStrategy.NONE and
                task_exec.retry_count < task.max_retries):
                task_exec.retry_count += 1
                await asyncio.sleep(task.retry_delay_seconds / 100)  # Simulated
                await self._run_task(execution_id, task_id)
                return
            else:
                execution.status = ExecutionStatus.FAILED
                execution.error_message = f"Task {task.name} failed: {str(e)}"
                return
                
        task_exec.completed_at = datetime.now()
        task_exec.duration_seconds = (
            task_exec.completed_at - task_exec.started_at
        ).total_seconds()
        
        # Run next tasks
        next_task_id = self._get_next_task(task, task_exec.output_data)
        if next_task_id:
            await self._run_task(execution_id, next_task_id)
            
    def _get_next_task(self, task: Task, output: Dict[str, Any]) -> Optional[str]:
        """Получение следующей задачи"""
        if not task.next_tasks:
            return None
            
        if task.task_type == TaskType.DECISION:
            # Evaluate condition
            result = output.get("decision_result", False)
            if result and len(task.next_tasks) > 0:
                return task.next_tasks[0]
            elif len(task.next_tasks) > 1:
                return task.next_tasks[1]
        else:
            return task.next_tasks[0] if task.next_tasks else None
            
        return None
        
    async def _handle_action(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка действия"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return {"action_result": "completed", "task_name": task.name}
        
    async def _handle_decision(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка решения"""
        # Simulate condition evaluation
        result = random.choice([True, False])
        return {"decision_result": result}
        
    async def _handle_parallel(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка параллельного выполнения"""
        await asyncio.sleep(random.uniform(0.05, 0.15))
        return {"parallel_completed": True}
        
    async def _handle_wait(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка ожидания"""
        wait_time = task.config.get("wait_seconds", 1)
        await asyncio.sleep(wait_time / 100)
        return {"wait_completed": True}
        
    async def _handle_notification(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка уведомления"""
        return {"notification_sent": True, "channel": task.config.get("channel", "email")}
        
    async def _handle_http(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка HTTP запроса"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return {"http_status": 200, "response": "ok"}
        
    async def _handle_script(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка скрипта"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return {"script_result": "success", "output": "Script executed"}
        
    async def _handle_approval(self, task: Task, input_data: Dict) -> Dict[str, Any]:
        """Обработка одобрения"""
        # Simulate approval (auto-approve for demo)
        return {"approved": True, "approver": "auto"}
        
    async def create_trigger(self, workflow_id: str,
                            trigger_type: TriggerType,
                            config: Dict[str, Any] = None) -> Optional[Trigger]:
        """Создание триггера"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        trigger = Trigger(
            trigger_id=f"trg_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            config=config or {}
        )
        
        self.triggers[trigger.trigger_id] = trigger
        return trigger
        
    async def fire_trigger(self, trigger_id: str,
                          input_data: Dict[str, Any] = None) -> Optional[WorkflowExecution]:
        """Активация триггера"""
        trigger = self.triggers.get(trigger_id)
        if not trigger or not trigger.is_active:
            return None
            
        trigger.trigger_count += 1
        trigger.last_triggered = datetime.now()
        
        return await self.execute_workflow(
            trigger.workflow_id,
            input_data,
            triggered_by=trigger.trigger_type.value
        )
        
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Статус выполнения"""
        execution = self.executions.get(execution_id)
        if not execution:
            return {}
            
        workflow = self.workflows.get(execution.workflow_id)
        
        tasks_status = {}
        for task_id, task_exec in execution.task_executions.items():
            task = workflow.tasks.get(task_id) if workflow else None
            tasks_status[task_id] = {
                "name": task.name if task else "Unknown",
                "status": task_exec.status.value,
                "duration": task_exec.duration_seconds
            }
            
        return {
            "execution_id": execution_id,
            "workflow": workflow.name if workflow else "Unknown",
            "status": execution.status.value,
            "current_task": execution.current_task_id,
            "tasks_completed": sum(1 for t in execution.task_executions.values() 
                                  if t.status == ExecutionStatus.COMPLETED),
            "tasks_total": len(workflow.tasks) if workflow else 0,
            "tasks_status": tasks_status,
            "duration": execution.duration_seconds,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "triggered_by": execution.triggered_by
        }
        
    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Детали workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {}
            
        tasks_info = []
        for task in workflow.tasks.values():
            tasks_info.append({
                "task_id": task.task_id,
                "name": task.name,
                "type": task.task_type.value,
                "next": task.next_tasks
            })
            
        executions = [
            e for e in self.executions.values()
            if e.workflow_id == workflow_id
        ]
        
        success_rate = 0
        if executions:
            completed = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
            success_rate = completed / len(executions) * 100
            
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value,
            "version": workflow.version,
            "tasks_count": len(workflow.tasks),
            "tasks": tasks_info,
            "start_task": workflow.start_task_id,
            "trigger_type": workflow.trigger_type.value,
            "execution_count": workflow.execution_count,
            "success_rate": success_rate
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = {}
        for wf in self.workflows.values():
            by_status[wf.status.value] = by_status.get(wf.status.value, 0) + 1
            
        exec_by_status = {}
        total_duration = 0
        for ex in self.executions.values():
            exec_by_status[ex.status.value] = exec_by_status.get(ex.status.value, 0) + 1
            total_duration += ex.duration_seconds
            
        trigger_by_type = {}
        for t in self.triggers.values():
            trigger_by_type[t.trigger_type.value] = trigger_by_type.get(t.trigger_type.value, 0) + 1
            
        return {
            "total_workflows": len(self.workflows),
            "by_status": by_status,
            "total_executions": len(self.executions),
            "executions_by_status": exec_by_status,
            "total_triggers": len(self.triggers),
            "triggers_by_type": trigger_by_type,
            "avg_execution_time": total_duration / max(len(self.executions), 1),
            "total_execution_time": total_duration
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 311: Workflow Engine Platform")
    print("=" * 60)
    
    engine = WorkflowEngine()
    print("✓ Workflow Engine created")
    
    # Create workflows
    print("\n📋 Creating Workflows...")
    
    # Workflow 1: Incident Response
    wf1 = await engine.create_workflow(
        "Incident Response",
        "Automated incident response workflow",
        "user_001",
        TriggerType.EVENT
    )
    
    # Add tasks
    t1 = await engine.add_task(wf1.workflow_id, "Receive Alert", TaskType.ACTION, {"source": "alertmanager"})
    t2 = await engine.add_task(wf1.workflow_id, "Check Severity", TaskType.DECISION, {"threshold": "critical"})
    t3 = await engine.add_task(wf1.workflow_id, "Page On-Call", TaskType.NOTIFICATION, {"channel": "pagerduty"})
    t4 = await engine.add_task(wf1.workflow_id, "Create Ticket", TaskType.ACTION, {"system": "jira"})
    t5 = await engine.add_task(wf1.workflow_id, "Run Diagnostics", TaskType.SCRIPT, {"script": "diagnose.sh"})
    t6 = await engine.add_task(wf1.workflow_id, "Auto Remediate", TaskType.ACTION, {"type": "restart"})
    t7 = await engine.add_task(wf1.workflow_id, "Notify Team", TaskType.NOTIFICATION, {"channel": "slack"})
    
    # Connect tasks
    await engine.connect_tasks(wf1.workflow_id, t1.task_id, t2.task_id)
    await engine.connect_tasks(wf1.workflow_id, t2.task_id, t3.task_id)  # Critical
    await engine.connect_tasks(wf1.workflow_id, t2.task_id, t4.task_id)  # Non-critical
    await engine.connect_tasks(wf1.workflow_id, t3.task_id, t5.task_id)
    await engine.connect_tasks(wf1.workflow_id, t4.task_id, t5.task_id)
    await engine.connect_tasks(wf1.workflow_id, t5.task_id, t6.task_id)
    await engine.connect_tasks(wf1.workflow_id, t6.task_id, t7.task_id)
    
    await engine.activate_workflow(wf1.workflow_id)
    print(f"  📋 {wf1.name}: {len(wf1.tasks)} tasks")
    
    # Workflow 2: Deployment Pipeline
    wf2 = await engine.create_workflow(
        "Deployment Pipeline",
        "CI/CD deployment workflow",
        "user_001",
        TriggerType.WEBHOOK
    )
    
    dt1 = await engine.add_task(wf2.workflow_id, "Checkout Code", TaskType.ACTION)
    dt2 = await engine.add_task(wf2.workflow_id, "Run Tests", TaskType.SCRIPT, {"script": "npm test"})
    dt3 = await engine.add_task(wf2.workflow_id, "Build Image", TaskType.ACTION, {"type": "docker"})
    dt4 = await engine.add_task(wf2.workflow_id, "Security Scan", TaskType.ACTION, {"scanner": "trivy"})
    dt5 = await engine.add_task(wf2.workflow_id, "Request Approval", TaskType.APPROVAL, {"approvers": ["lead"]})
    dt6 = await engine.add_task(wf2.workflow_id, "Deploy to Staging", TaskType.ACTION, {"env": "staging"})
    dt7 = await engine.add_task(wf2.workflow_id, "Run Integration Tests", TaskType.SCRIPT)
    dt8 = await engine.add_task(wf2.workflow_id, "Deploy to Production", TaskType.ACTION, {"env": "prod"})
    dt9 = await engine.add_task(wf2.workflow_id, "Notify Success", TaskType.NOTIFICATION, {"channel": "slack"})
    
    await engine.connect_tasks(wf2.workflow_id, dt1.task_id, dt2.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt2.task_id, dt3.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt3.task_id, dt4.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt4.task_id, dt5.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt5.task_id, dt6.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt6.task_id, dt7.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt7.task_id, dt8.task_id)
    await engine.connect_tasks(wf2.workflow_id, dt8.task_id, dt9.task_id)
    
    await engine.activate_workflow(wf2.workflow_id)
    print(f"  📋 {wf2.name}: {len(wf2.tasks)} tasks")
    
    # Workflow 3: User Onboarding
    wf3 = await engine.create_workflow(
        "User Onboarding",
        "New user setup workflow",
        "user_002",
        TriggerType.MANUAL
    )
    
    ot1 = await engine.add_task(wf3.workflow_id, "Create User Account", TaskType.ACTION)
    ot2 = await engine.add_task(wf3.workflow_id, "Assign Groups", TaskType.ACTION)
    ot3 = await engine.add_task(wf3.workflow_id, "Setup Email", TaskType.HTTP_REQUEST)
    ot4 = await engine.add_task(wf3.workflow_id, "Provision Tools", TaskType.PARALLEL)
    ot5 = await engine.add_task(wf3.workflow_id, "Send Welcome Email", TaskType.NOTIFICATION)
    
    await engine.connect_tasks(wf3.workflow_id, ot1.task_id, ot2.task_id)
    await engine.connect_tasks(wf3.workflow_id, ot2.task_id, ot3.task_id)
    await engine.connect_tasks(wf3.workflow_id, ot3.task_id, ot4.task_id)
    await engine.connect_tasks(wf3.workflow_id, ot4.task_id, ot5.task_id)
    
    await engine.activate_workflow(wf3.workflow_id)
    print(f"  📋 {wf3.name}: {len(wf3.tasks)} tasks")
    
    # Create more workflows
    workflows_data = [
        ("Change Request", "ITIL change management", "user_002"),
        ("Server Provisioning", "Automated server setup", "user_001"),
        ("Backup Verification", "Daily backup check", "user_003")
    ]
    
    for name, desc, owner in workflows_data:
        wf = await engine.create_workflow(name, desc, owner, TriggerType.SCHEDULE)
        
        # Add simple tasks
        t1 = await engine.add_task(wf.workflow_id, "Start", TaskType.ACTION)
        t2 = await engine.add_task(wf.workflow_id, "Process", TaskType.SCRIPT)
        t3 = await engine.add_task(wf.workflow_id, "Complete", TaskType.NOTIFICATION)
        
        await engine.connect_tasks(wf.workflow_id, t1.task_id, t2.task_id)
        await engine.connect_tasks(wf.workflow_id, t2.task_id, t3.task_id)
        
        await engine.activate_workflow(wf.workflow_id)
        print(f"  📋 {name}: {len(wf.tasks)} tasks")
        
    # Create triggers
    print("\n⚡ Creating Triggers...")
    
    triggers_data = [
        (wf1.workflow_id, TriggerType.EVENT, {"event": "alert.fired"}),
        (wf2.workflow_id, TriggerType.WEBHOOK, {"path": "/deploy"}),
        (wf3.workflow_id, TriggerType.MANUAL, {})
    ]
    
    triggers = []
    for wf_id, t_type, config in triggers_data:
        trigger = await engine.create_trigger(wf_id, t_type, config)
        triggers.append(trigger)
        wf = engine.workflows.get(wf_id)
        print(f"  ⚡ {wf.name}: {t_type.value}")
        
    # Execute workflows
    print("\n▶️ Executing Workflows...")
    
    executions = []
    
    # Execute via triggers
    for trigger in triggers:
        for _ in range(random.randint(2, 5)):
            exec_result = await engine.fire_trigger(
                trigger.trigger_id,
                {"input": "test_data"}
            )
            if exec_result:
                executions.append(exec_result)
                
    # Execute directly
    for _ in range(10):
        wf = random.choice(list(engine.workflows.values()))
        if wf.status == WorkflowStatus.ACTIVE:
            exec_result = await engine.execute_workflow(
                wf.workflow_id,
                {"data": f"test_{random.randint(1, 100)}"},
                f"user_{random.randint(1, 5):03d}"
            )
            if exec_result:
                executions.append(exec_result)
                
    completed = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
    failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
    print(f"  ✓ Executed {len(executions)} workflows: {completed} completed, {failed} failed")
    
    # Workflow details
    print("\n📋 Workflow Details:")
    
    for wf_id in list(engine.workflows.keys())[:3]:
        details = engine.get_workflow_details(wf_id)
        
        print(f"\n  📋 {details['name']}")
        print(f"     Status: {details['status']} | Version: {details['version']}")
        print(f"     Tasks: {details['tasks_count']} | Executions: {details['execution_count']}")
        print(f"     Success Rate: {details['success_rate']:.1f}%")
        
        if details['tasks']:
            print(f"     Task Flow:")
            for task in details['tasks'][:5]:
                next_str = f" -> {task['next'][0][:8]}..." if task['next'] else ""
                print(f"       [{task['type']:10}] {task['name']}{next_str}")
                
    # Execution status
    print("\n▶️ Recent Executions:")
    
    print("\n  ┌─────────────────────────────┬────────────────────┬────────────┬──────────┐")
    print("  │ Workflow                    │ Status             │ Tasks      │ Duration │")
    print("  ├─────────────────────────────┼────────────────────┼────────────┼──────────┤")
    
    for execution in list(engine.executions.values())[:8]:
        status = engine.get_execution_status(execution.execution_id)
        
        wf_name = status['workflow'][:27].ljust(27)
        exec_status = status['status'][:18].ljust(18)
        tasks = f"{status['tasks_completed']}/{status['tasks_total']}".ljust(10)
        duration = f"{status['duration']:.2f}s".ljust(8)
        
        print(f"  │ {wf_name} │ {exec_status} │ {tasks} │ {duration} │")
        
    print("  └─────────────────────────────┴────────────────────┴────────────┴──────────┘")
    
    # Workflow list
    print("\n📋 Workflow List:")
    
    print("\n  ┌───────────────────────────────┬────────────┬───────┬───────────┬─────────┐")
    print("  │ Workflow                      │ Status     │ Tasks │ Exec      │ Success │")
    print("  ├───────────────────────────────┼────────────┼───────┼───────────┼─────────┤")
    
    for wf in engine.workflows.values():
        details = engine.get_workflow_details(wf.workflow_id)
        
        name = wf.name[:29].ljust(29)
        status = wf.status.value[:10].ljust(10)
        tasks = str(len(wf.tasks)).ljust(5)
        execs = str(wf.execution_count).ljust(9)
        success = f"{details['success_rate']:.0f}%".ljust(7)
        
        print(f"  │ {name} │ {status} │ {tasks} │ {execs} │ {success} │")
        
    print("  └───────────────────────────────┴────────────┴───────┴───────────┴─────────┘")
    
    # Trigger status
    print("\n⚡ Trigger Status:")
    
    for trigger in triggers:
        wf = engine.workflows.get(trigger.workflow_id)
        active = "✓" if trigger.is_active else "✗"
        last = trigger.last_triggered.strftime('%H:%M:%S') if trigger.last_triggered else "Never"
        
        print(f"  [{active}] {wf.name}: {trigger.trigger_type.value}")
        print(f"      Triggered: {trigger.trigger_count}x | Last: {last}")
        
    # Execution status distribution
    print("\n📊 Execution Status Distribution:")
    
    stats = engine.get_statistics()
    
    for status_name, count in stats['executions_by_status'].items():
        bar = "█" * min(count, 15) + "░" * (15 - min(count, 15))
        icon = "✓" if status_name == "completed" else "✗" if status_name == "failed" else "○"
        print(f"  {icon} {status_name:12} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Engine Statistics:")
    
    print(f"\n  Total Workflows: {stats['total_workflows']}")
    print("  By Status:")
    for status, count in stats['by_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Total Executions: {stats['total_executions']}")
    print(f"  Avg Execution Time: {stats['avg_execution_time']:.3f}s")
    print(f"  Total Execution Time: {stats['total_execution_time']:.2f}s")
    
    print(f"\n  Total Triggers: {stats['total_triggers']}")
    print("  By Type:")
    for t_type, count in stats['triggers_by_type'].items():
        print(f"    {t_type}: {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Workflow Engine Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Workflows:             {stats['total_workflows']:>12}                          │")
    print(f"│ Total Executions:            {stats['total_executions']:>12}                          │")
    print(f"│ Total Triggers:              {stats['total_triggers']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Avg Execution Time:          {stats['avg_execution_time']:>10.3f}s                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Workflow Engine Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
