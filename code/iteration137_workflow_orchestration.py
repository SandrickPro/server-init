#!/usr/bin/env python3
"""
Server Init - Iteration 137: Workflow Orchestration Platform
Платформа Workflow Orchestration

Функционал:
- Workflow Definition - определение воркфлоу
- Task Execution - выполнение задач
- DAG Processing - обработка DAG
- Parallel Execution - параллельное выполнение
- Error Handling - обработка ошибок
- Retry Mechanisms - механизмы повторов
- State Management - управление состоянием
- Event Triggers - триггеры событий
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
from collections import defaultdict
import uuid


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkflowStatus(Enum):
    """Статус воркфлоу"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """Тип триггера"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    DEPENDENCY = "dependency"


@dataclass
class RetryPolicy:
    """Политика повторов"""
    max_retries: int = 3
    retry_delay_seconds: int = 60
    exponential_backoff: bool = True
    max_delay_seconds: int = 3600


@dataclass
class Task:
    """Задача"""
    task_id: str
    name: str = ""
    description: str = ""
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Config
    timeout_seconds: int = 3600
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    
    # Execution
    executor: str = "default"  # default, docker, kubernetes, lambda
    command: str = ""
    parameters: Dict = field(default_factory=dict)
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Results
    output: Any = None
    error_message: str = ""
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Retries
    retry_count: int = 0


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    instance_id: str
    task_id: str = ""
    run_id: str = ""
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Results
    output: Any = None
    error_message: str = ""
    
    # Timing
    queued_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retries
    retry_count: int = 0


@dataclass
class Workflow:
    """Воркфлоу"""
    workflow_id: str
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    # Tasks
    tasks: List[Task] = field(default_factory=list)
    
    # Status
    status: WorkflowStatus = WorkflowStatus.DRAFT
    
    # Trigger
    trigger_type: TriggerType = TriggerType.MANUAL
    schedule: str = ""  # cron expression
    
    # Config
    concurrency: int = 10
    timeout_seconds: int = 86400
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowRun:
    """Запуск воркфлоу"""
    run_id: str
    workflow_id: str = ""
    
    # Status
    status: WorkflowStatus = WorkflowStatus.RUNNING
    
    # Task instances
    task_instances: Dict[str, TaskInstance] = field(default_factory=dict)
    
    # Parameters
    parameters: Dict = field(default_factory=dict)
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Results
    tasks_completed: int = 0
    tasks_failed: int = 0


@dataclass
class Trigger:
    """Триггер"""
    trigger_id: str
    workflow_id: str = ""
    
    # Type
    trigger_type: TriggerType = TriggerType.MANUAL
    
    # Config
    schedule: str = ""  # cron
    event_type: str = ""
    webhook_path: str = ""
    
    # Status
    enabled: bool = True
    last_triggered: Optional[datetime] = None


class DAGProcessor:
    """Обработчик DAG"""
    
    def __init__(self):
        self.execution_order: Dict[str, List[List[str]]] = {}
        
    def build_dag(self, workflow: Workflow) -> Dict[str, Set[str]]:
        """Построение DAG"""
        dag = {}
        
        for task in workflow.tasks:
            dag[task.task_id] = set(task.dependencies)
            
        return dag
        
    def topological_sort(self, workflow: Workflow) -> List[List[str]]:
        """Топологическая сортировка (уровневая)"""
        dag = self.build_dag(workflow)
        task_ids = {t.task_id for t in workflow.tasks}
        
        levels = []
        remaining = set(task_ids)
        completed = set()
        
        while remaining:
            # Find tasks with all dependencies completed
            level = []
            for task_id in remaining:
                deps = dag.get(task_id, set())
                if deps.issubset(completed):
                    level.append(task_id)
                    
            if not level:
                # Circular dependency detected
                raise ValueError("Circular dependency detected in workflow")
                
            levels.append(level)
            completed.update(level)
            remaining -= set(level)
            
        self.execution_order[workflow.workflow_id] = levels
        return levels
        
    def validate_dag(self, workflow: Workflow) -> Dict:
        """Валидация DAG"""
        issues = []
        
        task_ids = {t.task_id for t in workflow.tasks}
        
        # Check for missing dependencies
        for task in workflow.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    issues.append(f"Task {task.task_id} has unknown dependency: {dep}")
                    
        # Check for circular dependencies
        try:
            self.topological_sort(workflow)
        except ValueError as e:
            issues.append(str(e))
            
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


class TaskExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, executor_type: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[executor_type] = handler
        
    async def execute(self, task: Task, parameters: Dict = None) -> TaskInstance:
        """Выполнение задачи"""
        instance = TaskInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            handler = self.handlers.get(task.executor, self._default_handler)
            
            # Merge parameters
            exec_params = {**task.parameters, **(parameters or {})}
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(task, exec_params),
                timeout=task.timeout_seconds
            )
            
            instance.status = TaskStatus.SUCCESS
            instance.output = result
            
        except asyncio.TimeoutError:
            instance.status = TaskStatus.FAILED
            instance.error_message = f"Task timed out after {task.timeout_seconds}s"
            
        except Exception as e:
            instance.status = TaskStatus.FAILED
            instance.error_message = str(e)
            
        finally:
            instance.completed_at = datetime.now()
            
        return instance
        
    async def _default_handler(self, task: Task, parameters: Dict) -> Any:
        """Обработчик по умолчанию"""
        # Simulate task execution
        await asyncio.sleep(0.1)
        return {"status": "completed", "task": task.name}


class RetryManager:
    """Менеджер повторов"""
    
    def __init__(self, executor: TaskExecutor):
        self.executor = executor
        
    async def execute_with_retry(self, task: Task, parameters: Dict = None) -> TaskInstance:
        """Выполнение с повторами"""
        policy = task.retry_policy
        delay = policy.retry_delay_seconds
        
        for attempt in range(policy.max_retries + 1):
            instance = await self.executor.execute(task, parameters)
            instance.retry_count = attempt
            
            if instance.status == TaskStatus.SUCCESS:
                return instance
                
            if attempt < policy.max_retries:
                # Wait before retry
                await asyncio.sleep(delay)
                
                # Exponential backoff
                if policy.exponential_backoff:
                    delay = min(delay * 2, policy.max_delay_seconds)
                    
        return instance


class WorkflowEngine:
    """Движок воркфлоу"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.runs: Dict[str, WorkflowRun] = {}
        self.dag_processor = DAGProcessor()
        self.executor = TaskExecutor()
        self.retry_manager = RetryManager(self.executor)
        
        # Register default handler
        self.executor.register_handler("default", self._default_task_handler)
        
    async def _default_task_handler(self, task: Task, parameters: Dict) -> Dict:
        """Обработчик задач по умолчанию"""
        await asyncio.sleep(0.05)  # Simulate work
        return {
            "task_id": task.task_id,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        
    def create_workflow(self, name: str, description: str = "", **kwargs) -> Workflow:
        """Создание воркфлоу"""
        workflow = Workflow(
            workflow_id=f"wf_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            **kwargs
        )
        self.workflows[workflow.workflow_id] = workflow
        return workflow
        
    def add_task(self, workflow_id: str, name: str, dependencies: List[str] = None,
                  **kwargs) -> Task:
        """Добавление задачи"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            dependencies=dependencies or [],
            **kwargs
        )
        workflow.tasks.append(task)
        workflow.updated_at = datetime.now()
        return task
        
    async def run(self, workflow_id: str, parameters: Dict = None) -> WorkflowRun:
        """Запуск воркфлоу"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        # Validate DAG
        validation = self.dag_processor.validate_dag(workflow)
        if not validation["valid"]:
            raise ValueError(f"Invalid workflow: {validation['issues']}")
            
        # Create run
        run = WorkflowRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            parameters=parameters or {}
        )
        self.runs[run.run_id] = run
        
        # Get execution order
        levels = self.dag_processor.topological_sort(workflow)
        
        # Execute tasks level by level
        task_map = {t.task_id: t for t in workflow.tasks}
        
        for level in levels:
            # Execute tasks in parallel within each level
            tasks_to_run = [task_map[task_id] for task_id in level]
            
            instances = await asyncio.gather(*[
                self.retry_manager.execute_with_retry(task, run.parameters)
                for task in tasks_to_run
            ])
            
            # Store results
            for instance in instances:
                run.task_instances[instance.task_id] = instance
                
                if instance.status == TaskStatus.SUCCESS:
                    run.tasks_completed += 1
                else:
                    run.tasks_failed += 1
                    
            # Check for failures
            if run.tasks_failed > 0:
                run.status = WorkflowStatus.FAILED
                break
                
        if run.tasks_failed == 0:
            run.status = WorkflowStatus.COMPLETED
            
        run.completed_at = datetime.now()
        return run
        
    def pause(self, run_id: str) -> bool:
        """Приостановка"""
        run = self.runs.get(run_id)
        if run and run.status == WorkflowStatus.RUNNING:
            run.status = WorkflowStatus.PAUSED
            return True
        return False
        
    def cancel(self, run_id: str) -> bool:
        """Отмена"""
        run = self.runs.get(run_id)
        if run and run.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
            run.status = WorkflowStatus.CANCELLED
            return True
        return False


class TriggerManager:
    """Менеджер триггеров"""
    
    def __init__(self, engine: WorkflowEngine):
        self.engine = engine
        self.triggers: Dict[str, Trigger] = {}
        
    def add_trigger(self, workflow_id: str, trigger_type: TriggerType,
                     **kwargs) -> Trigger:
        """Добавление триггера"""
        trigger = Trigger(
            trigger_id=f"trigger_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            **kwargs
        )
        self.triggers[trigger.trigger_id] = trigger
        return trigger
        
    async def fire(self, trigger_id: str, parameters: Dict = None) -> WorkflowRun:
        """Активация триггера"""
        trigger = self.triggers.get(trigger_id)
        if not trigger or not trigger.enabled:
            return None
            
        trigger.last_triggered = datetime.now()
        return await self.engine.run(trigger.workflow_id, parameters)
        
    def get_triggers(self, workflow_id: str) -> List[Trigger]:
        """Получение триггеров воркфлоу"""
        return [t for t in self.triggers.values() if t.workflow_id == workflow_id]


class StateManager:
    """Менеджер состояния"""
    
    def __init__(self):
        self.state: Dict[str, Dict] = {}
        
    def set(self, run_id: str, key: str, value: Any):
        """Установка состояния"""
        if run_id not in self.state:
            self.state[run_id] = {}
        self.state[run_id][key] = value
        
    def get(self, run_id: str, key: str = None) -> Any:
        """Получение состояния"""
        run_state = self.state.get(run_id, {})
        if key:
            return run_state.get(key)
        return run_state
        
    def clear(self, run_id: str):
        """Очистка состояния"""
        self.state.pop(run_id, None)


class WorkflowOrchestrationPlatform:
    """Платформа оркестрации воркфлоу"""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        self.trigger_manager = TriggerManager(self.engine)
        self.state_manager = StateManager()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        runs = list(self.engine.runs.values())
        
        return {
            "workflows": len(self.engine.workflows),
            "total_runs": len(runs),
            "completed_runs": len([r for r in runs if r.status == WorkflowStatus.COMPLETED]),
            "failed_runs": len([r for r in runs if r.status == WorkflowStatus.FAILED]),
            "running_runs": len([r for r in runs if r.status == WorkflowStatus.RUNNING]),
            "triggers": len(self.trigger_manager.triggers),
            "total_tasks": sum(len(w.tasks) for w in self.engine.workflows.values())
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 137: Workflow Orchestration Platform")
    print("=" * 60)
    
    async def demo():
        platform = WorkflowOrchestrationPlatform()
        print("✓ Workflow Orchestration Platform created")
        
        # Create workflow
        print("\n📋 Creating Workflow...")
        
        workflow = platform.engine.create_workflow(
            "data-pipeline",
            "ETL data processing pipeline",
            tags=["etl", "data", "daily"]
        )
        
        print(f"  ✓ {workflow.name} ({workflow.workflow_id})")
        
        # Add tasks
        print("\n📦 Adding Tasks...")
        
        # Extract task
        extract_task = platform.engine.add_task(
            workflow.workflow_id,
            "extract-data",
            dependencies=[],
            timeout_seconds=600,
            parameters={"source": "database", "query": "SELECT * FROM orders"}
        )
        
        # Transform tasks (parallel)
        transform_task1 = platform.engine.add_task(
            workflow.workflow_id,
            "transform-orders",
            dependencies=[extract_task.task_id],
            parameters={"type": "orders"}
        )
        
        transform_task2 = platform.engine.add_task(
            workflow.workflow_id,
            "transform-customers",
            dependencies=[extract_task.task_id],
            parameters={"type": "customers"}
        )
        
        # Aggregate task
        aggregate_task = platform.engine.add_task(
            workflow.workflow_id,
            "aggregate-data",
            dependencies=[transform_task1.task_id, transform_task2.task_id],
            parameters={"output": "summary"}
        )
        
        # Load task
        load_task = platform.engine.add_task(
            workflow.workflow_id,
            "load-to-warehouse",
            dependencies=[aggregate_task.task_id],
            parameters={"destination": "data-warehouse"}
        )
        
        # Notify task
        notify_task = platform.engine.add_task(
            workflow.workflow_id,
            "send-notification",
            dependencies=[load_task.task_id],
            parameters={"channel": "slack"}
        )
        
        for task in workflow.tasks:
            deps = ", ".join(task.dependencies) if task.dependencies else "none"
            print(f"  ✓ {task.name} (depends on: {deps})")
            
        # Validate DAG
        print("\n🔍 Validating DAG...")
        
        validation = platform.engine.dag_processor.validate_dag(workflow)
        
        if validation["valid"]:
            print("  ✓ DAG is valid")
        else:
            for issue in validation["issues"]:
                print(f"  ✗ {issue}")
                
        # Get execution order
        print("\n📊 Execution Order (levels):")
        
        levels = platform.engine.dag_processor.topological_sort(workflow)
        
        task_map = {t.task_id: t.name for t in workflow.tasks}
        
        for i, level in enumerate(levels):
            task_names = [task_map[tid] for tid in level]
            parallel = " || " if len(task_names) > 1 else ""
            print(f"  Level {i + 1}: {parallel.join(task_names)}")
            
        # Add triggers
        print("\n⚡ Adding Triggers...")
        
        manual_trigger = platform.trigger_manager.add_trigger(
            workflow.workflow_id,
            TriggerType.MANUAL
        )
        
        scheduled_trigger = platform.trigger_manager.add_trigger(
            workflow.workflow_id,
            TriggerType.SCHEDULED,
            schedule="0 2 * * *"  # Daily at 2 AM
        )
        
        webhook_trigger = platform.trigger_manager.add_trigger(
            workflow.workflow_id,
            TriggerType.WEBHOOK,
            webhook_path="/api/trigger/data-pipeline"
        )
        
        print(f"  ✓ Manual trigger")
        print(f"  ✓ Scheduled trigger (0 2 * * *)")
        print(f"  ✓ Webhook trigger (/api/trigger/data-pipeline)")
        
        # Run workflow
        print("\n🚀 Running Workflow...")
        
        run = await platform.engine.run(
            workflow.workflow_id,
            parameters={"date": "2024-01-15"}
        )
        
        print(f"  Run ID: {run.run_id}")
        print(f"  Status: {run.status.value}")
        print(f"  Tasks Completed: {run.tasks_completed}")
        print(f"  Tasks Failed: {run.tasks_failed}")
        
        # Task results
        print("\n📋 Task Results:")
        
        for task_id, instance in run.task_instances.items():
            task = task_map.get(task_id, task_id)
            icon = "✓" if instance.status == TaskStatus.SUCCESS else "✗"
            print(f"  {icon} {task}: {instance.status.value}")
            
            if instance.completed_at and instance.started_at:
                duration = (instance.completed_at - instance.started_at).total_seconds()
                print(f"     Duration: {duration:.2f}s")
                
        # State management
        print("\n💾 State Management:")
        
        platform.state_manager.set(run.run_id, "processed_records", 15000)
        platform.state_manager.set(run.run_id, "output_path", "/data/output/2024-01-15")
        
        state = platform.state_manager.get(run.run_id)
        
        for key, value in state.items():
            print(f"  {key}: {value}")
            
        # Create another workflow with parallel branches
        print("\n📋 Creating Parallel Workflow...")
        
        parallel_wf = platform.engine.create_workflow(
            "parallel-processing",
            "Parallel data processing workflow"
        )
        
        # Start task
        start = platform.engine.add_task(parallel_wf.workflow_id, "start")
        
        # Parallel branches
        branch_tasks = []
        for i in range(4):
            branch = platform.engine.add_task(
                parallel_wf.workflow_id,
                f"branch-{i + 1}",
                dependencies=[start.task_id]
            )
            branch_tasks.append(branch)
            
        # Join task
        join = platform.engine.add_task(
            parallel_wf.workflow_id,
            "join",
            dependencies=[t.task_id for t in branch_tasks]
        )
        
        # End task
        end = platform.engine.add_task(
            parallel_wf.workflow_id,
            "end",
            dependencies=[join.task_id]
        )
        
        print(f"  ✓ {parallel_wf.name}: {len(parallel_wf.tasks)} tasks")
        
        # Run parallel workflow
        print("\n🚀 Running Parallel Workflow...")
        
        parallel_run = await platform.engine.run(parallel_wf.workflow_id)
        
        print(f"  Status: {parallel_run.status.value}")
        print(f"  Tasks: {parallel_run.tasks_completed}/{len(parallel_wf.tasks)}")
        
        # Workflow with retry
        print("\n🔄 Testing Retry Mechanism...")
        
        retry_wf = platform.engine.create_workflow("retry-test", "Test retry")
        
        retry_task = platform.engine.add_task(
            retry_wf.workflow_id,
            "flaky-task",
            retry_policy=RetryPolicy(
                max_retries=3,
                retry_delay_seconds=1,
                exponential_backoff=True
            )
        )
        
        print(f"  ✓ Task with {retry_task.retry_policy.max_retries} max retries")
        
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Workflows: {stats['workflows']}")
        print(f"  Total Tasks: {stats['total_tasks']}")
        print(f"  Triggers: {stats['triggers']}")
        print(f"  Total Runs: {stats['total_runs']}")
        print(f"    Completed: {stats['completed_runs']}")
        print(f"    Failed: {stats['failed_runs']}")
        print(f"    Running: {stats['running_runs']}")
        
        # Dashboard
        print("\n📋 Workflow Orchestration Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │            Workflow Orchestration Overview                  │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Workflows:          {stats['workflows']:>10}                        │")
        print(f"  │ Total Tasks:        {stats['total_tasks']:>10}                        │")
        print(f"  │ Triggers:           {stats['triggers']:>10}                        │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Runs:         {stats['total_runs']:>10}                        │")
        print(f"  │   Completed:        {stats['completed_runs']:>10}                        │")
        print(f"  │   Failed:           {stats['failed_runs']:>10}                        │")
        print(f"  │   Running:          {stats['running_runs']:>10}                        │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Visual workflow representation
        print("\n🔀 Data Pipeline Visualization:")
        print("  ┌──────────────┐")
        print("  │ extract-data │")
        print("  └──────┬───────┘")
        print("         │")
        print("    ┌────┴────┐")
        print("    ▼         ▼")
        print("┌──────────┐ ┌──────────────┐")
        print("│transform │ │transform     │")
        print("│-orders   │ │-customers    │")
        print("└────┬─────┘ └──────┬───────┘")
        print("     │              │")
        print("     └──────┬───────┘")
        print("            ▼")
        print("    ┌──────────────┐")
        print("    │aggregate-data│")
        print("    └──────┬───────┘")
        print("           ▼")
        print("  ┌────────────────┐")
        print("  │load-to-warehouse│")
        print("  └────────┬───────┘")
        print("           ▼")
        print("  ┌─────────────────┐")
        print("  │send-notification│")
        print("  └─────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Workflow Orchestration Platform initialized!")
    print("=" * 60)
