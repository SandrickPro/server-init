#!/usr/bin/env python3
"""
Server Init - Iteration 228: Workflow Engine Platform
Платформа workflow-движка

Функционал:
- Workflow Definition - определение workflows
- DAG Management - управление DAG
- State Machine - машина состояний
- Task Scheduling - планирование задач
- Retry & Compensation - повторы и компенсация
- Event Handling - обработка событий
- Execution History - история выполнения
- Monitoring & Alerts - мониторинг и алерты
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkflowStatus(Enum):
    """Статус workflow"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"


class RetryStrategy(Enum):
    """Стратегия повторов"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_def_id: str
    name: str = ""
    description: str = ""
    
    # Handler
    handler: str = ""  # Function name or endpoint
    timeout_seconds: int = 300
    
    # Retry
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_delay_seconds: int = 10
    
    # Input/Output
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTask:
    """Задача workflow"""
    task_id: str
    workflow_id: str = ""
    task_def_id: str = ""
    
    # Position in DAG
    dependencies: List[str] = field(default_factory=list)
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Retry
    attempt: int = 0
    error_message: str = ""
    
    # Times
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0


@dataclass
class WorkflowDefinition:
    """Определение workflow"""
    definition_id: str
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Tasks
    tasks: List[TaskDefinition] = field(default_factory=list)
    
    # DAG
    dag_edges: List[tuple] = field(default_factory=list)  # (from_task, to_task)
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    schedule: str = ""  # Cron expression
    
    # Settings
    max_parallel_tasks: int = 10
    timeout_seconds: int = 3600
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowExecution:
    """Выполнение workflow"""
    execution_id: str
    definition_id: str = ""
    
    # Status
    status: WorkflowStatus = WorkflowStatus.CREATED
    
    # Tasks
    tasks: List[WorkflowTask] = field(default_factory=list)
    
    # Input/Output
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Progress
    completed_tasks: int = 0
    total_tasks: int = 0
    
    # Error
    error_message: str = ""
    
    # Times
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Trigger info
    triggered_by: str = ""
    trigger_type: TriggerType = TriggerType.MANUAL


@dataclass
class ExecutionEvent:
    """Событие выполнения"""
    event_id: str
    execution_id: str = ""
    task_id: str = ""
    
    event_type: str = ""  # task_started, task_completed, task_failed, etc.
    details: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: datetime = field(default_factory=datetime.now)


class DAGValidator:
    """Валидатор DAG"""
    
    def validate(self, tasks: List[TaskDefinition],
                edges: List[tuple]) -> tuple:
        """Валидация DAG"""
        # Check for cycles using DFS
        task_names = {t.name for t in tasks}
        graph = {name: [] for name in task_names}
        
        for from_task, to_task in edges:
            if from_task in graph:
                graph[from_task].append(to_task)
                
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
                    
            rec_stack.remove(node)
            return False
            
        for node in task_names:
            if node not in visited:
                if has_cycle(node):
                    return False, "Cycle detected in DAG"
                    
        return True, "Valid DAG"


class TaskScheduler:
    """Планировщик задач"""
    
    def __init__(self):
        self.queue: List[WorkflowTask] = []
        
    def schedule(self, task: WorkflowTask):
        """Планирование задачи"""
        task.status = TaskStatus.SCHEDULED
        task.scheduled_at = datetime.now()
        self.queue.append(task)
        
    def get_ready_tasks(self, execution: WorkflowExecution) -> List[WorkflowTask]:
        """Получение готовых задач"""
        completed_ids = {t.task_id for t in execution.tasks 
                        if t.status == TaskStatus.COMPLETED}
        
        ready = []
        for task in execution.tasks:
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            deps_met = all(dep in completed_ids for dep in task.dependencies)
            if deps_met:
                ready.append(task)
                
        return ready


class WorkflowEngine:
    """Движок workflow"""
    
    def __init__(self):
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.events: List[ExecutionEvent] = []
        self.scheduler = TaskScheduler()
        self.validator = DAGValidator()
        
    def create_definition(self, name: str, description: str = "") -> WorkflowDefinition:
        """Создание определения workflow"""
        definition = WorkflowDefinition(
            definition_id=f"wf_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description
        )
        self.definitions[definition.definition_id] = definition
        return definition
        
    def add_task(self, definition_id: str, name: str, handler: str,
                timeout: int = 300, dependencies: List[str] = None) -> Optional[TaskDefinition]:
        """Добавление задачи"""
        definition = self.definitions.get(definition_id)
        if not definition:
            return None
            
        task_def = TaskDefinition(
            task_def_id=f"td_{uuid.uuid4().hex[:8]}",
            name=name,
            handler=handler,
            timeout_seconds=timeout
        )
        
        definition.tasks.append(task_def)
        
        # Add edges for dependencies
        if dependencies:
            for dep in dependencies:
                definition.dag_edges.append((dep, name))
                
        return task_def
        
    def validate_workflow(self, definition_id: str) -> tuple:
        """Валидация workflow"""
        definition = self.definitions.get(definition_id)
        if not definition:
            return False, "Definition not found"
            
        return self.validator.validate(definition.tasks, definition.dag_edges)
        
    def start_execution(self, definition_id: str,
                       input_data: Dict[str, Any] = None,
                       triggered_by: str = "system") -> Optional[WorkflowExecution]:
        """Запуск выполнения"""
        definition = self.definitions.get(definition_id)
        if not definition:
            return None
            
        execution = WorkflowExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            definition_id=definition_id,
            input_data=input_data or {},
            triggered_by=triggered_by,
            trigger_type=definition.trigger_type
        )
        
        # Create task instances
        task_map = {}
        for task_def in definition.tasks:
            task = WorkflowTask(
                task_id=f"task_{uuid.uuid4().hex[:8]}",
                workflow_id=execution.execution_id,
                task_def_id=task_def.task_def_id
            )
            task_map[task_def.name] = task.task_id
            execution.tasks.append(task)
            
        # Set dependencies using task IDs
        for i, task_def in enumerate(definition.tasks):
            deps = []
            for from_task, to_task in definition.dag_edges:
                if to_task == task_def.name and from_task in task_map:
                    deps.append(task_map[from_task])
            execution.tasks[i].dependencies = deps
            
        execution.total_tasks = len(execution.tasks)
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now()
        
        self.executions[execution.execution_id] = execution
        
        self._log_event(execution.execution_id, "", "workflow_started", {})
        
        return execution
        
    def execute_task(self, execution_id: str, task_id: str) -> bool:
        """Выполнение задачи"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
            
        task = next((t for t in execution.tasks if t.task_id == task_id), None)
        if not task:
            return False
            
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.attempt += 1
        
        self._log_event(execution_id, task_id, "task_started", {"attempt": task.attempt})
        
        # Simulate execution
        success = random.random() > 0.1  # 90% success rate
        
        if success:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.duration_seconds = (task.completed_at - task.started_at).total_seconds()
            task.output_data = {"result": "success"}
            
            execution.completed_tasks += 1
            self._log_event(execution_id, task_id, "task_completed", {})
        else:
            task.status = TaskStatus.FAILED
            task.error_message = "Simulated failure"
            self._log_event(execution_id, task_id, "task_failed", {"error": task.error_message})
            
        return success
        
    def run_workflow(self, execution_id: str) -> bool:
        """Запуск workflow до завершения"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
            
        while execution.status == WorkflowStatus.RUNNING:
            ready_tasks = self.scheduler.get_ready_tasks(execution)
            
            if not ready_tasks:
                # Check if all tasks completed
                if execution.completed_tasks == execution.total_tasks:
                    execution.status = WorkflowStatus.COMPLETED
                else:
                    # Check for failed tasks
                    failed = any(t.status == TaskStatus.FAILED for t in execution.tasks)
                    if failed:
                        execution.status = WorkflowStatus.FAILED
                    else:
                        execution.status = WorkflowStatus.COMPLETED
                break
                
            for task in ready_tasks:
                self.execute_task(execution_id, task.task_id)
                
        execution.completed_at = datetime.now()
        if execution.started_at:
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            
        self._log_event(execution_id, "", "workflow_completed", 
                       {"status": execution.status.value})
        
        return execution.status == WorkflowStatus.COMPLETED
        
    def _log_event(self, execution_id: str, task_id: str,
                  event_type: str, details: Dict[str, Any]):
        """Логирование события"""
        event = ExecutionEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            execution_id=execution_id,
            task_id=task_id,
            event_type=event_type,
            details=details
        )
        self.events.append(event)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        executions = list(self.executions.values())
        completed = [e for e in executions if e.status == WorkflowStatus.COMPLETED]
        failed = [e for e in executions if e.status == WorkflowStatus.FAILED]
        
        avg_duration = sum(e.duration_seconds for e in completed) / len(completed) if completed else 0
        
        return {
            "total_definitions": len(self.definitions),
            "total_executions": len(executions),
            "completed_executions": len(completed),
            "failed_executions": len(failed),
            "avg_duration_seconds": avg_duration,
            "total_events": len(self.events)
        }


class WorkflowEnginePlatform:
    """Платформа workflow-движка"""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        
    def create_workflow(self, name: str, description: str = "") -> WorkflowDefinition:
        """Создание workflow"""
        return self.engine.create_definition(name, description)
        
    def add_task(self, workflow_id: str, name: str, handler: str,
                dependencies: List[str] = None) -> Optional[TaskDefinition]:
        """Добавление задачи"""
        return self.engine.add_task(workflow_id, name, handler, 300, dependencies)
        
    def start(self, workflow_id: str, input_data: Dict[str, Any] = None) -> Optional[WorkflowExecution]:
        """Запуск workflow"""
        return self.engine.start_execution(workflow_id, input_data)
        
    def run(self, execution_id: str) -> bool:
        """Выполнение workflow"""
        return self.engine.run_workflow(execution_id)


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 228: Workflow Engine Platform")
    print("=" * 60)
    
    platform = WorkflowEnginePlatform()
    print("✓ Workflow Engine Platform created")
    
    # Create workflows
    print("\n📋 Creating Workflow Definitions...")
    
    # Workflow 1: Data Pipeline
    wf1 = platform.create_workflow("data_pipeline", "ETL data pipeline workflow")
    wf1.trigger_type = TriggerType.SCHEDULE
    wf1.schedule = "0 * * * *"  # Every hour
    
    platform.add_task(wf1.definition_id, "extract", "extract_handler")
    platform.add_task(wf1.definition_id, "validate", "validate_handler", ["extract"])
    platform.add_task(wf1.definition_id, "transform", "transform_handler", ["validate"])
    platform.add_task(wf1.definition_id, "load", "load_handler", ["transform"])
    platform.add_task(wf1.definition_id, "notify", "notify_handler", ["load"])
    
    print(f"  ✓ {wf1.name}: {len(wf1.tasks)} tasks")
    
    # Workflow 2: Deployment Pipeline
    wf2 = platform.create_workflow("deployment_pipeline", "CI/CD deployment workflow")
    wf2.trigger_type = TriggerType.WEBHOOK
    
    platform.add_task(wf2.definition_id, "build", "build_handler")
    platform.add_task(wf2.definition_id, "test", "test_handler", ["build"])
    platform.add_task(wf2.definition_id, "security_scan", "scan_handler", ["build"])
    platform.add_task(wf2.definition_id, "deploy_staging", "deploy_handler", ["test", "security_scan"])
    platform.add_task(wf2.definition_id, "integration_test", "int_test_handler", ["deploy_staging"])
    platform.add_task(wf2.definition_id, "deploy_prod", "deploy_handler", ["integration_test"])
    
    print(f"  ✓ {wf2.name}: {len(wf2.tasks)} tasks")
    
    # Workflow 3: User Onboarding
    wf3 = platform.create_workflow("user_onboarding", "New user onboarding workflow")
    wf3.trigger_type = TriggerType.EVENT
    
    platform.add_task(wf3.definition_id, "create_account", "account_handler")
    platform.add_task(wf3.definition_id, "send_welcome", "email_handler", ["create_account"])
    platform.add_task(wf3.definition_id, "setup_defaults", "setup_handler", ["create_account"])
    platform.add_task(wf3.definition_id, "notify_team", "slack_handler", ["send_welcome", "setup_defaults"])
    
    print(f"  ✓ {wf3.name}: {len(wf3.tasks)} tasks")
    
    # Validate workflows
    print("\n✅ Validating Workflows...")
    
    for wf in [wf1, wf2, wf3]:
        valid, msg = platform.engine.validate_workflow(wf.definition_id)
        status = "✓" if valid else "✗"
        print(f"  {status} {wf.name}: {msg}")
        
    # Run executions
    print("\n🚀 Running Workflow Executions...")
    
    executions = []
    
    # Run data pipeline multiple times
    for i in range(3):
        exec = platform.start(wf1.definition_id, {"batch_id": i + 1})
        if exec:
            platform.run(exec.execution_id)
            executions.append(exec)
            status_icon = "✓" if exec.status == WorkflowStatus.COMPLETED else "✗"
            print(f"  {status_icon} {wf1.name} run {i+1}: {exec.status.value}")
            
    # Run deployment pipeline
    exec = platform.start(wf2.definition_id, {"commit": "abc123"})
    if exec:
        platform.run(exec.execution_id)
        executions.append(exec)
        status_icon = "✓" if exec.status == WorkflowStatus.COMPLETED else "✗"
        print(f"  {status_icon} {wf2.name}: {exec.status.value}")
        
    # Run user onboarding
    for i in range(2):
        exec = platform.start(wf3.definition_id, {"user_id": f"user_{i+1}"})
        if exec:
            platform.run(exec.execution_id)
            executions.append(exec)
            status_icon = "✓" if exec.status == WorkflowStatus.COMPLETED else "✗"
            print(f"  {status_icon} {wf3.name} run {i+1}: {exec.status.value}")
            
    # Display workflows
    print("\n📋 Workflow Definitions:")
    
    print("\n  ┌────────────────────────┬────────┬──────────────┬───────────────┐")
    print("  │ Workflow               │ Tasks  │ Trigger      │ Version       │")
    print("  ├────────────────────────┼────────┼──────────────┼───────────────┤")
    
    for wf in platform.engine.definitions.values():
        name = wf.name[:20].ljust(20)
        tasks = str(len(wf.tasks))[:6].ljust(6)
        trigger = wf.trigger_type.value[:12].ljust(12)
        version = wf.version[:13].ljust(13)
        
        print(f"  │ {name} │ {tasks} │ {trigger} │ {version} │")
        
    print("  └────────────────────────┴────────┴──────────────┴───────────────┘")
    
    # DAG visualization
    print("\n🔀 DAG Structure:")
    
    for wf in [wf1, wf2]:
        print(f"\n  {wf.name}:")
        
        # Build dependency tree
        task_deps = {}
        for task in wf.tasks:
            deps = [from_t for from_t, to_t in wf.dag_edges if to_t == task.name]
            task_deps[task.name] = deps
            
        for task in wf.tasks:
            deps = task_deps.get(task.name, [])
            if deps:
                print(f"    {' + '.join(deps)} -> {task.name}")
            else:
                print(f"    [start] -> {task.name}")
                
    # Execution history
    print("\n📜 Execution History:")
    
    print("\n  ┌────────────────────────┬────────────┬──────────┬────────────┐")
    print("  │ Execution              │ Status     │ Tasks    │ Duration   │")
    print("  ├────────────────────────┼────────────┼──────────┼────────────┤")
    
    for exec in platform.engine.executions.values():
        wf = platform.engine.definitions.get(exec.definition_id)
        name = (wf.name if wf else "unknown")[:20].ljust(20)
        
        status_icons = {
            WorkflowStatus.COMPLETED: "🟢",
            WorkflowStatus.FAILED: "🔴",
            WorkflowStatus.RUNNING: "🔵",
            WorkflowStatus.PAUSED: "🟡",
            WorkflowStatus.CANCELLED: "⚪"
        }
        status = f"{status_icons.get(exec.status, '⚪')}"[:10].ljust(10)
        
        tasks = f"{exec.completed_tasks}/{exec.total_tasks}"[:8].ljust(8)
        duration = f"{exec.duration_seconds:.1f}s"[:10].ljust(10)
        
        print(f"  │ {name} │ {status} │ {tasks} │ {duration} │")
        
    print("  └────────────────────────┴────────────┴──────────┴────────────┘")
    
    # Task breakdown for first execution
    if executions:
        exec = executions[0]
        wf = platform.engine.definitions.get(exec.definition_id)
        
        print(f"\n📊 Task Breakdown: {wf.name if wf else 'unknown'}")
        
        for task in exec.tasks:
            task_def = next((t for t in wf.tasks if t.task_def_id == task.task_def_id), None)
            name = task_def.name if task_def else "unknown"
            
            status_icons = {
                TaskStatus.COMPLETED: "✓",
                TaskStatus.FAILED: "✗",
                TaskStatus.RUNNING: "→",
                TaskStatus.PENDING: "○"
            }
            icon = status_icons.get(task.status, "?")
            
            print(f"    {icon} {name}: {task.status.value} ({task.duration_seconds:.2f}s)")
            
    # Events timeline
    print("\n📝 Recent Events:")
    
    for event in platform.engine.events[-8:]:
        time_str = event.timestamp.strftime("%H:%M:%S")
        print(f"  [{time_str}] {event.event_type}")
        
    # Statistics
    print("\n📈 Platform Statistics:")
    
    stats = platform.engine.get_statistics()
    
    print(f"\n  Definitions: {stats['total_definitions']}")
    print(f"  Executions: {stats['total_executions']}")
    print(f"  Completed: {stats['completed_executions']}")
    print(f"  Failed: {stats['failed_executions']}")
    print(f"  Avg Duration: {stats['avg_duration_seconds']:.2f}s")
    
    # Success rate
    total = stats['completed_executions'] + stats['failed_executions']
    success_rate = (stats['completed_executions'] / total * 100) if total > 0 else 0
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                       Workflow Engine Dashboard                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Workflow Definitions:          {stats['total_definitions']:>12}                        │")
    print(f"│ Total Executions:              {stats['total_executions']:>12}                        │")
    print(f"│ Completed:                     {stats['completed_executions']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                    {success_rate:>10.1f}%                       │")
    print(f"│ Avg Duration (seconds):          {stats['avg_duration_seconds']:>10.2f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Workflow Engine Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
