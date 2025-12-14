#!/usr/bin/env python3
"""
Server Init - Iteration 119: Workflow Orchestration Platform
Платформа оркестрации рабочих процессов

Функционал:
- Workflow Definition - определение воркфлоу
- Task Execution - выполнение задач
- DAG Management - управление DAG
- Scheduling - планирование
- Dependencies - зависимости
- State Machine - машина состояний
- Retry Policies - политики повторов
- Monitoring - мониторинг выполнения
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from collections import defaultdict
import uuid
import random


class WorkflowStatus(Enum):
    """Статус воркфлоу"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    WAITING = "waiting"  # Ожидание зависимостей
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class TaskType(Enum):
    """Тип задачи"""
    SHELL = "shell"
    PYTHON = "python"
    HTTP = "http"
    SQL = "sql"
    BRANCH = "branch"
    JOIN = "join"
    NOTIFY = "notify"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    WEBHOOK = "webhook"
    API = "api"


class RetryStrategy(Enum):
    """Стратегия повтора"""
    NONE = "none"
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryPolicy:
    """Политика повторов"""
    strategy: RetryStrategy = RetryStrategy.FIXED
    max_retries: int = 3
    initial_delay_sec: int = 5
    max_delay_sec: int = 300
    backoff_multiplier: float = 2.0


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str = ""
    
    # Type
    task_type: TaskType = TaskType.SHELL
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Retry
    retry_policy: Optional[RetryPolicy] = None
    
    # Timeout
    timeout_sec: int = 3600
    
    # Condition
    run_condition: str = ""  # Expression to evaluate


@dataclass
class TaskExecution:
    """Выполнение задачи"""
    execution_id: str
    task_id: str = ""
    task_name: str = ""
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Timing
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Results
    output: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    
    # Retries
    attempt: int = 1
    max_attempts: int = 1


@dataclass
class WorkflowDefinition:
    """Определение воркфлоу"""
    workflow_id: str
    name: str = ""
    description: str = ""
    
    # Tasks (DAG)
    tasks: Dict[str, TaskDefinition] = field(default_factory=dict)
    
    # Schedule
    trigger_type: TriggerType = TriggerType.MANUAL
    schedule: str = ""  # cron expression
    
    # Settings
    max_concurrent_tasks: int = 10
    timeout_sec: int = 86400
    
    # Defaults
    default_retry_policy: Optional[RetryPolicy] = None
    
    # Version
    version: int = 1
    active: bool = True


@dataclass
class WorkflowExecution:
    """Выполнение воркфлоу"""
    run_id: str
    workflow_id: str = ""
    workflow_name: str = ""
    
    # Status
    status: WorkflowStatus = WorkflowStatus.PENDING
    
    # Tasks
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Context
    input_params: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    
    # Triggered by
    trigger: TriggerType = TriggerType.MANUAL
    triggered_by: str = ""


@dataclass
class ScheduleEntry:
    """Запись расписания"""
    schedule_id: str
    workflow_id: str = ""
    
    # Cron
    cron_expression: str = ""
    
    # Next run
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    
    # Status
    enabled: bool = True


class DAGManager:
    """Менеджер DAG"""
    
    def __init__(self):
        pass
        
    def validate_dag(self, tasks: Dict[str, TaskDefinition]) -> Dict[str, Any]:
        """Валидация DAG"""
        errors = []
        
        # Check for unknown dependencies
        all_task_ids = set(tasks.keys())
        for task_id, task in tasks.items():
            for dep in task.depends_on:
                if dep not in all_task_ids:
                    errors.append(f"Task '{task_id}' depends on unknown task '{dep}'")
                    
        # Check for cycles
        cycles = self._detect_cycles(tasks)
        if cycles:
            errors.append(f"Cycle detected: {' -> '.join(cycles)}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "task_count": len(tasks)
        }
        
    def _detect_cycles(self, tasks: Dict[str, TaskDefinition]) -> List[str]:
        """Обнаружение циклов"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {task_id: WHITE for task_id in tasks}
        path = []
        
        def dfs(task_id: str) -> bool:
            color[task_id] = GRAY
            path.append(task_id)
            
            task = tasks.get(task_id)
            if task:
                for dep in task.depends_on:
                    if color.get(dep, WHITE) == GRAY:
                        # Found cycle
                        cycle_start = path.index(dep)
                        return path[cycle_start:]
                    if color.get(dep, WHITE) == WHITE:
                        result = dfs(dep)
                        if result:
                            return result
                            
            color[task_id] = BLACK
            path.pop()
            return []
            
        for task_id in tasks:
            if color[task_id] == WHITE:
                result = dfs(task_id)
                if result:
                    return result
                    
        return []
        
    def get_execution_order(self, tasks: Dict[str, TaskDefinition]) -> List[List[str]]:
        """Получение порядка выполнения (топологическая сортировка по уровням)"""
        in_degree = {task_id: 0 for task_id in tasks}
        
        for task in tasks.values():
            for dep in task.depends_on:
                if dep in in_degree:
                    in_degree[task.task_id] = in_degree.get(task.task_id, 0) + 1
                    
        levels = []
        remaining = set(tasks.keys())
        
        while remaining:
            # Get tasks with no dependencies
            ready = [t for t in remaining if in_degree[t] == 0]
            if not ready:
                break  # Cycle detected
                
            levels.append(ready)
            
            for task_id in ready:
                remaining.remove(task_id)
                # Decrease in-degree for dependent tasks
                for other_id, other in tasks.items():
                    if task_id in other.depends_on:
                        in_degree[other_id] -= 1
                        
        return levels


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.handlers: Dict[TaskType, Callable] = {}
        self._register_handlers()
        
    def _register_handlers(self):
        """Регистрация обработчиков"""
        self.handlers[TaskType.SHELL] = self._execute_shell
        self.handlers[TaskType.PYTHON] = self._execute_python
        self.handlers[TaskType.HTTP] = self._execute_http
        self.handlers[TaskType.SQL] = self._execute_sql
        self.handlers[TaskType.NOTIFY] = self._execute_notify
        
    async def _execute_shell(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Shell задача"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return {"exit_code": 0, "output": f"Executed: {config.get('command', '')}"}
        
    async def _execute_python(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Python задача"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return {"result": f"Python script executed: {config.get('script', '')}"}
        
    async def _execute_http(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP задача"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return {"status": 200, "url": config.get("url", "")}
        
    async def _execute_sql(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """SQL задача"""
        await asyncio.sleep(random.uniform(0.1, 0.5))
        return {"rows_affected": random.randint(1, 100), "query": config.get("query", "")}
        
    async def _execute_notify(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Notify задача"""
        await asyncio.sleep(0.1)
        return {"sent": True, "channel": config.get("channel", "")}
        
    async def execute(self, task: TaskDefinition, context: Dict[str, Any] = None) -> TaskExecution:
        """Выполнение задачи"""
        execution = TaskExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            task_name=task.name,
            started_at=datetime.now()
        )
        
        try:
            execution.status = TaskStatus.RUNNING
            
            handler = self.handlers.get(task.task_type)
            if handler:
                result = await handler(task.config)
                execution.output = result
                execution.status = TaskStatus.SUCCESS
            else:
                execution.status = TaskStatus.FAILED
                execution.error = f"No handler for task type: {task.task_type.value}"
                
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.error = str(e)
            
        execution.finished_at = datetime.now()
        return execution


class WorkflowEngine:
    """Движок воркфлоу"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.dag_manager = DAGManager()
        self.task_executor = TaskExecutor()
        
    def create_workflow(self, name: str, description: str = "",
                         **kwargs) -> WorkflowDefinition:
        """Создание воркфлоу"""
        workflow = WorkflowDefinition(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            **kwargs
        )
        self.workflows[workflow.workflow_id] = workflow
        return workflow
        
    def add_task(self, workflow_id: str, name: str,
                  task_type: TaskType = TaskType.SHELL,
                  depends_on: List[str] = None,
                  **kwargs) -> TaskDefinition:
        """Добавление задачи"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        task = TaskDefinition(
            task_id=f"task_{len(workflow.tasks) + 1}",
            name=name,
            task_type=task_type,
            depends_on=depends_on or [],
            **kwargs
        )
        
        workflow.tasks[task.task_id] = task
        return task
        
    async def execute_workflow(self, workflow_id: str,
                                params: Dict[str, Any] = None,
                                trigger: TriggerType = TriggerType.MANUAL) -> WorkflowExecution:
        """Выполнение воркфлоу"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        # Validate DAG
        validation = self.dag_manager.validate_dag(workflow.tasks)
        if not validation["valid"]:
            return None
            
        # Create execution
        run = WorkflowExecution(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            workflow_name=workflow.name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            input_params=params or {},
            trigger=trigger
        )
        
        self.executions[run.run_id] = run
        
        # Get execution order
        levels = self.dag_manager.get_execution_order(workflow.tasks)
        
        # Execute tasks level by level
        try:
            for level in levels:
                # Execute tasks in parallel within level
                tasks_to_run = [workflow.tasks[task_id] for task_id in level]
                
                executions = await asyncio.gather(
                    *[self.task_executor.execute(task, run.input_params) 
                      for task in tasks_to_run]
                )
                
                # Store executions
                for exec_result in executions:
                    run.task_executions[exec_result.task_id] = exec_result
                    
                    if exec_result.status == TaskStatus.FAILED:
                        run.status = WorkflowStatus.FAILED
                        run.finished_at = datetime.now()
                        return run
                        
            run.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            run.status = WorkflowStatus.FAILED
            
        run.finished_at = datetime.now()
        return run


class ScheduleManager:
    """Менеджер расписания"""
    
    def __init__(self, engine: WorkflowEngine):
        self.engine = engine
        self.schedules: Dict[str, ScheduleEntry] = {}
        
    def create_schedule(self, workflow_id: str,
                         cron_expression: str) -> ScheduleEntry:
        """Создание расписания"""
        schedule = ScheduleEntry(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            next_run=datetime.now() + timedelta(hours=1)
        )
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def get_due_schedules(self) -> List[ScheduleEntry]:
        """Получение готовых к выполнению"""
        now = datetime.now()
        return [s for s in self.schedules.values()
                if s.enabled and s.next_run and s.next_run <= now]


class WorkflowOrchestrationPlatform:
    """Платформа оркестрации"""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        self.scheduler = ScheduleManager(self.engine)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        executions = list(self.engine.executions.values())
        
        status_counts = defaultdict(int)
        for run in executions:
            status_counts[run.status.value] += 1
            
        return {
            "total_workflows": len(self.engine.workflows),
            "total_executions": len(executions),
            "executions_by_status": dict(status_counts),
            "scheduled_workflows": len(self.scheduler.schedules)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 119: Workflow Orchestration Platform")
    print("=" * 60)
    
    async def demo():
        platform = WorkflowOrchestrationPlatform()
        print("✓ Workflow Orchestration Platform created")
        
        # Create workflows
        print("\n📋 Creating Workflows...")
        
        # CI/CD Pipeline
        cicd = platform.engine.create_workflow(
            "CI/CD Pipeline",
            "Build, test and deploy pipeline",
            trigger_type=TriggerType.WEBHOOK
        )
        
        # Add tasks
        tasks_data = [
            ("Checkout Code", TaskType.SHELL, [], {"command": "git checkout"}),
            ("Install Dependencies", TaskType.SHELL, ["task_1"], {"command": "npm install"}),
            ("Run Lint", TaskType.SHELL, ["task_2"], {"command": "npm run lint"}),
            ("Run Tests", TaskType.SHELL, ["task_2"], {"command": "npm test"}),
            ("Build", TaskType.SHELL, ["task_3", "task_4"], {"command": "npm run build"}),
            ("Deploy to Staging", TaskType.SHELL, ["task_5"], {"command": "deploy staging"}),
            ("Run E2E Tests", TaskType.SHELL, ["task_6"], {"command": "npm run e2e"}),
            ("Deploy to Production", TaskType.SHELL, ["task_7"], {"command": "deploy prod"}),
            ("Notify Team", TaskType.NOTIFY, ["task_8"], {"channel": "slack"})
        ]
        
        for name, ttype, deps, config in tasks_data:
            platform.engine.add_task(
                cicd.workflow_id, name, ttype,
                depends_on=deps, config=config
            )
            
        print(f"  ✓ {cicd.name}: {len(cicd.tasks)} tasks")
        
        # Data Pipeline
        data_pipeline = platform.engine.create_workflow(
            "Data Pipeline",
            "ETL data processing",
            trigger_type=TriggerType.SCHEDULE
        )
        
        data_tasks = [
            ("Extract from Source", TaskType.SQL, [], {"query": "SELECT * FROM source"}),
            ("Transform Data", TaskType.PYTHON, ["task_1"], {"script": "transform.py"}),
            ("Load to DWH", TaskType.SQL, ["task_2"], {"query": "INSERT INTO dwh"}),
            ("Generate Report", TaskType.PYTHON, ["task_3"], {"script": "report.py"}),
            ("Send Report", TaskType.NOTIFY, ["task_4"], {"channel": "email"})
        ]
        
        for name, ttype, deps, config in data_tasks:
            platform.engine.add_task(
                data_pipeline.workflow_id, name, ttype,
                depends_on=deps, config=config
            )
            
        print(f"  ✓ {data_pipeline.name}: {len(data_pipeline.tasks)} tasks")
        
        # ML Training Pipeline
        ml_pipeline = platform.engine.create_workflow(
            "ML Training Pipeline",
            "Model training and deployment"
        )
        
        ml_tasks = [
            ("Fetch Dataset", TaskType.HTTP, [], {"url": "http://data/dataset"}),
            ("Preprocess", TaskType.PYTHON, ["task_1"], {"script": "preprocess.py"}),
            ("Feature Engineering", TaskType.PYTHON, ["task_2"], {"script": "features.py"}),
            ("Train Model", TaskType.PYTHON, ["task_3"], {"script": "train.py"}),
            ("Evaluate Model", TaskType.PYTHON, ["task_4"], {"script": "evaluate.py"}),
            ("Deploy Model", TaskType.SHELL, ["task_5"], {"command": "deploy model"})
        ]
        
        for name, ttype, deps, config in ml_tasks:
            platform.engine.add_task(
                ml_pipeline.workflow_id, name, ttype,
                depends_on=deps, config=config
            )
            
        print(f"  ✓ {ml_pipeline.name}: {len(ml_pipeline.tasks)} tasks")
        
        # Validate DAGs
        print("\n🔍 Validating DAGs...")
        
        for wf in platform.engine.workflows.values():
            validation = platform.engine.dag_manager.validate_dag(wf.tasks)
            status = "✓" if validation["valid"] else "✗"
            print(f"  {status} {wf.name}: {validation['task_count']} tasks")
            
        # Show execution order
        print("\n📊 Execution Order (CI/CD Pipeline):")
        
        levels = platform.engine.dag_manager.get_execution_order(cicd.tasks)
        for i, level in enumerate(levels):
            task_names = [cicd.tasks[t].name for t in level]
            print(f"  Level {i+1}: {', '.join(task_names)}")
            
        # Execute workflows
        print("\n🚀 Executing Workflows...")
        
        workflows_to_run = [cicd, data_pipeline, ml_pipeline]
        
        for wf in workflows_to_run:
            print(f"\n  Running: {wf.name}...")
            
            run = await platform.engine.execute_workflow(
                wf.workflow_id,
                {"env": "staging"},
                TriggerType.MANUAL
            )
            
            if run:
                status_icon = "✓" if run.status == WorkflowStatus.COMPLETED else "✗"
                duration = (run.finished_at - run.started_at).total_seconds()
                
                print(f"    {status_icon} Status: {run.status.value}")
                print(f"    ⏱️ Duration: {duration:.2f}s")
                
                # Task summary
                success = sum(1 for t in run.task_executions.values() if t.status == TaskStatus.SUCCESS)
                failed = sum(1 for t in run.task_executions.values() if t.status == TaskStatus.FAILED)
                
                print(f"    📊 Tasks: {success} success, {failed} failed")
                
        # Create schedules
        print("\n⏰ Creating Schedules...")
        
        schedules_data = [
            (data_pipeline.workflow_id, "0 */6 * * *", "Every 6 hours"),
            (ml_pipeline.workflow_id, "0 0 * * 0", "Weekly on Sunday"),
        ]
        
        for wf_id, cron, desc in schedules_data:
            schedule = platform.scheduler.create_schedule(wf_id, cron)
            wf = platform.engine.workflows.get(wf_id)
            print(f"  ✓ {wf.name}: {cron} ({desc})")
            
        # Execution history
        print("\n📜 Execution History:")
        
        for run in list(platform.engine.executions.values())[:5]:
            status_icon = {"completed": "✓", "failed": "✗", "running": "⟳"}.get(run.status.value, "?")
            duration = (run.finished_at - run.started_at).total_seconds() if run.finished_at else 0
            print(f"  {status_icon} {run.workflow_name}: {run.status.value} ({duration:.2f}s)")
            
        # Task execution details
        print("\n📝 Task Execution Details (CI/CD):")
        
        cicd_run = next((r for r in platform.engine.executions.values() 
                        if r.workflow_name == "CI/CD Pipeline"), None)
        if cicd_run:
            for task_id, exec_result in cicd_run.task_executions.items():
                task = cicd.tasks.get(task_id)
                if task:
                    status_icon = "✓" if exec_result.status == TaskStatus.SUCCESS else "✗"
                    duration = (exec_result.finished_at - exec_result.started_at).total_seconds() if exec_result.finished_at else 0
                    print(f"    {status_icon} {task.name}: {exec_result.status.value} ({duration:.3f}s)")
                    
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Workflows:")
        print(f"    Total: {stats['total_workflows']}")
        print(f"    Scheduled: {stats['scheduled_workflows']}")
        
        print(f"\n  Executions:")
        print(f"    Total: {stats['total_executions']}")
        for status, count in stats['executions_by_status'].items():
            icon = {"completed": "✓", "failed": "✗"}.get(status, "?")
            print(f"    {icon} {status}: {count}")
            
        # Workflow complexity
        print("\n📈 Workflow Complexity:")
        
        for wf in platform.engine.workflows.values():
            task_count = len(wf.tasks)
            dep_count = sum(len(t.depends_on) for t in wf.tasks.values())
            levels = len(platform.engine.dag_manager.get_execution_order(wf.tasks))
            print(f"  {wf.name}: {task_count} tasks, {dep_count} deps, {levels} levels")
            
        # Dashboard
        print("\n📋 Workflow Orchestration Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │            Workflow Orchestration Overview                  │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Workflows:      {stats['total_workflows']:>10}                      │")
        print(f"  │ Total Executions:     {stats['total_executions']:>10}                      │")
        print(f"  │ Scheduled Workflows:  {stats['scheduled_workflows']:>10}                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Completed:            {stats['executions_by_status'].get('completed', 0):>10}                      │")
        print(f"  │ Failed:               {stats['executions_by_status'].get('failed', 0):>10}                      │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Workflow Orchestration Platform initialized!")
    print("=" * 60)
