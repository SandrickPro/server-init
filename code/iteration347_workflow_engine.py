#!/usr/bin/env python3
"""
Server Init - Iteration 347: Workflow Engine Platform
Платформа движка рабочих процессов

Функционал:
- Workflow Definition - определение процессов
- Task Execution - выполнение задач
- State Machine - машина состояний
- Parallel Execution - параллельное выполнение
- Conditional Logic - условная логика
- Timer Events - таймерные события
- Human Tasks - человеческие задачи
- Process Monitoring - мониторинг процессов
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import json


class WorkflowStatus(Enum):
    """Статус рабочего процесса"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Тип задачи"""
    SERVICE = "service"
    SCRIPT = "script"
    MANUAL = "manual"
    DECISION = "decision"
    SUBPROCESS = "subprocess"
    TIMER = "timer"
    MESSAGE = "message"
    SIGNAL = "signal"


class TaskStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class GatewayType(Enum):
    """Тип шлюза"""
    EXCLUSIVE = "exclusive"  # XOR
    PARALLEL = "parallel"  # AND
    INCLUSIVE = "inclusive"  # OR
    EVENT_BASED = "event_based"


class EventType(Enum):
    """Тип события"""
    START = "start"
    END = "end"
    INTERMEDIATE = "intermediate"
    BOUNDARY = "boundary"
    TIMER = "timer"
    MESSAGE = "message"
    SIGNAL = "signal"
    ERROR = "error"


class TransitionType(Enum):
    """Тип перехода"""
    SEQUENCE = "sequence"
    CONDITIONAL = "conditional"
    DEFAULT = "default"


class HumanTaskStatus(Enum):
    """Статус человеческой задачи"""
    CREATED = "created"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELEGATED = "delegated"
    ESCALATED = "escalated"


@dataclass
class WorkflowDefinition:
    """Определение рабочего процесса"""
    workflow_id: str
    name: str
    
    # Version
    version: int = 1
    
    # Description
    description: str = ""
    
    # Elements
    task_ids: List[str] = field(default_factory=list)
    gateway_ids: List[str] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)
    transition_ids: List[str] = field(default_factory=list)
    
    # Start/End
    start_event_id: str = ""
    end_event_ids: List[str] = field(default_factory=list)
    
    # Variables
    input_variables: Dict[str, Any] = field(default_factory=dict)
    output_variables: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    timeout_seconds: int = 0
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Status
    status: WorkflowStatus = WorkflowStatus.DRAFT
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


@dataclass
class TaskDefinition:
    """Определение задачи"""
    task_id: str
    name: str
    
    # Type
    task_type: TaskType = TaskType.SERVICE
    
    # Implementation
    implementation: str = ""  # Service name, script path, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Input/Output
    input_mappings: Dict[str, str] = field(default_factory=dict)
    output_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Retry
    retry_count: int = 0
    retry_interval_seconds: int = 60
    
    # Timeout
    timeout_seconds: int = 300
    
    # Boundary events
    boundary_event_ids: List[str] = field(default_factory=list)
    
    # Multi-instance
    is_multi_instance: bool = False
    collection_variable: str = ""
    
    # Human task
    assignee: str = ""
    candidate_groups: List[str] = field(default_factory=list)
    due_date_expression: str = ""
    
    # Description
    description: str = ""


@dataclass
class Gateway:
    """Шлюз"""
    gateway_id: str
    name: str
    
    # Type
    gateway_type: GatewayType = GatewayType.EXCLUSIVE
    
    # Default flow
    default_flow_id: str = ""
    
    # Description
    description: str = ""


@dataclass
class Event:
    """Событие"""
    event_id: str
    name: str
    
    # Type
    event_type: EventType = EventType.START
    
    # Trigger
    trigger_type: str = ""  # timer, message, signal, etc.
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    
    # Attached to
    attached_to_task_id: str = ""  # For boundary events
    is_interrupting: bool = True
    
    # Description
    description: str = ""


@dataclass
class Transition:
    """Переход"""
    transition_id: str
    name: str = ""
    
    # Source/Target
    source_id: str = ""
    target_id: str = ""
    
    # Type
    transition_type: TransitionType = TransitionType.SEQUENCE
    
    # Condition
    condition_expression: str = ""
    
    # Order (for evaluation)
    order: int = 0


@dataclass
class WorkflowInstance:
    """Экземпляр рабочего процесса"""
    instance_id: str
    workflow_id: str
    
    # Status
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    
    # Current position
    current_task_ids: List[str] = field(default_factory=list)
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # History
    completed_task_ids: List[str] = field(default_factory=list)
    
    # Initiator
    initiator: str = ""
    
    # Business key
    business_key: str = ""
    
    # Parent (for subprocesses)
    parent_instance_id: str = ""
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class TaskInstance:
    """Экземпляр задачи"""
    task_instance_id: str
    task_id: str
    instance_id: str
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution
    retry_count: int = 0
    
    # Variables
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Error
    error_message: str = ""
    
    # Assignee (for human tasks)
    assignee: str = ""
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class HumanTask:
    """Человеческая задача"""
    human_task_id: str
    task_instance_id: str
    
    # Assignment
    assignee: str = ""
    owner: str = ""
    candidate_users: List[str] = field(default_factory=list)
    candidate_groups: List[str] = field(default_factory=list)
    
    # Status
    status: HumanTaskStatus = HumanTaskStatus.CREATED
    
    # Priority
    priority: int = 50  # 0-100
    
    # Form
    form_key: str = ""
    form_data: Dict[str, Any] = field(default_factory=dict)
    
    # Due date
    due_date: Optional[datetime] = None
    
    # Comments
    comments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    claimed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class TimerEvent:
    """Таймерное событие"""
    timer_id: str
    event_id: str
    instance_id: str
    
    # Timer type
    timer_type: str = "duration"  # duration, date, cycle
    
    # Timer definition
    timer_definition: str = ""  # PT1H, 2024-01-01T00:00:00, R3/PT1H
    
    # Fire time
    fire_time: Optional[datetime] = None
    
    # Status
    is_fired: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessHistory:
    """История процесса"""
    history_id: str
    instance_id: str
    
    # Event
    event_type: str = ""  # task_started, task_completed, gateway_evaluated, etc.
    element_id: str = ""
    element_type: str = ""
    
    # Data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # User
    user_id: str = ""
    
    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowMetrics:
    """Метрики процесса"""
    metrics_id: str
    workflow_id: str
    
    # Instances
    total_instances: int = 0
    active_instances: int = 0
    completed_instances: int = 0
    failed_instances: int = 0
    
    # Duration
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    
    # Tasks
    avg_tasks_per_instance: float = 0.0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


class WorkflowEngine:
    """Движок рабочих процессов"""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.tasks: Dict[str, TaskDefinition] = {}
        self.gateways: Dict[str, Gateway] = {}
        self.events: Dict[str, Event] = {}
        self.transitions: Dict[str, Transition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.task_instances: Dict[str, TaskInstance] = {}
        self.human_tasks: Dict[str, HumanTask] = {}
        self.timer_events: Dict[str, TimerEvent] = {}
        self.history: Dict[str, ProcessHistory] = {}
        self.metrics: Dict[str, WorkflowMetrics] = {}
        
    async def create_workflow(self, name: str,
                             description: str = "",
                             category: str = "",
                             tags: List[str] = None,
                             timeout_seconds: int = 0) -> WorkflowDefinition:
        """Создание рабочего процесса"""
        workflow = WorkflowDefinition(
            workflow_id=f"wf_{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            timeout_seconds=timeout_seconds
        )
        
        self.workflows[workflow.workflow_id] = workflow
        return workflow
        
    async def add_task(self, workflow_id: str,
                      name: str,
                      task_type: TaskType,
                      implementation: str = "",
                      parameters: Dict[str, Any] = None,
                      timeout_seconds: int = 300,
                      retry_count: int = 0,
                      assignee: str = "",
                      candidate_groups: List[str] = None,
                      description: str = "") -> Optional[TaskDefinition]:
        """Добавление задачи"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        task = TaskDefinition(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            name=name,
            task_type=task_type,
            implementation=implementation,
            parameters=parameters or {},
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
            assignee=assignee,
            candidate_groups=candidate_groups or [],
            description=description
        )
        
        self.tasks[task.task_id] = task
        workflow.task_ids.append(task.task_id)
        workflow.updated_at = datetime.now()
        
        return task
        
    async def add_gateway(self, workflow_id: str,
                         name: str,
                         gateway_type: GatewayType,
                         default_flow_id: str = "",
                         description: str = "") -> Optional[Gateway]:
        """Добавление шлюза"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        gateway = Gateway(
            gateway_id=f"gw_{uuid.uuid4().hex[:8]}",
            name=name,
            gateway_type=gateway_type,
            default_flow_id=default_flow_id,
            description=description
        )
        
        self.gateways[gateway.gateway_id] = gateway
        workflow.gateway_ids.append(gateway.gateway_id)
        workflow.updated_at = datetime.now()
        
        return gateway
        
    async def add_event(self, workflow_id: str,
                       name: str,
                       event_type: EventType,
                       trigger_type: str = "",
                       trigger_config: Dict[str, Any] = None,
                       attached_to_task_id: str = "",
                       is_interrupting: bool = True,
                       description: str = "") -> Optional[Event]:
        """Добавление события"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            name=name,
            event_type=event_type,
            trigger_type=trigger_type,
            trigger_config=trigger_config or {},
            attached_to_task_id=attached_to_task_id,
            is_interrupting=is_interrupting,
            description=description
        )
        
        self.events[event.event_id] = event
        workflow.event_ids.append(event.event_id)
        
        if event_type == EventType.START:
            workflow.start_event_id = event.event_id
        elif event_type == EventType.END:
            workflow.end_event_ids.append(event.event_id)
            
        workflow.updated_at = datetime.now()
        
        return event
        
    async def add_transition(self, workflow_id: str,
                            source_id: str,
                            target_id: str,
                            name: str = "",
                            transition_type: TransitionType = TransitionType.SEQUENCE,
                            condition_expression: str = "",
                            order: int = 0) -> Optional[Transition]:
        """Добавление перехода"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        transition = Transition(
            transition_id=f"tr_{uuid.uuid4().hex[:8]}",
            name=name,
            source_id=source_id,
            target_id=target_id,
            transition_type=transition_type,
            condition_expression=condition_expression,
            order=order
        )
        
        self.transitions[transition.transition_id] = transition
        workflow.transition_ids.append(transition.transition_id)
        workflow.updated_at = datetime.now()
        
        return transition
        
    async def activate_workflow(self, workflow_id: str) -> bool:
        """Активация процесса"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.DRAFT:
            return False
            
        workflow.status = WorkflowStatus.ACTIVE
        workflow.updated_at = datetime.now()
        return True
        
    async def start_instance(self, workflow_id: str,
                            variables: Dict[str, Any] = None,
                            initiator: str = "",
                            business_key: str = "") -> Optional[WorkflowInstance]:
        """Запуск экземпляра процесса"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow.status != WorkflowStatus.ACTIVE:
            return None
            
        instance = WorkflowInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:12]}",
            workflow_id=workflow_id,
            variables=variables or {},
            initiator=initiator,
            business_key=business_key
        )
        
        self.instances[instance.instance_id] = instance
        
        # Start from start event
        if workflow.start_event_id:
            await self._process_element(instance, workflow.start_event_id)
            
        return instance
        
    async def _process_element(self, instance: WorkflowInstance, element_id: str):
        """Обработка элемента процесса"""
        workflow = self.workflows.get(instance.workflow_id)
        if not workflow:
            return
            
        # Record history
        await self._record_history(instance.instance_id, "element_entered", element_id)
        
        # Check element type
        if element_id in [t for t in workflow.task_ids]:
            await self._process_task(instance, element_id)
        elif element_id in [g for g in workflow.gateway_ids]:
            await self._process_gateway(instance, element_id)
        elif element_id in [e for e in workflow.event_ids]:
            await self._process_event(instance, element_id)
            
    async def _process_task(self, instance: WorkflowInstance, task_id: str):
        """Обработка задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return
            
        # Create task instance
        task_instance = TaskInstance(
            task_instance_id=f"ti_{uuid.uuid4().hex[:8]}",
            task_id=task_id,
            instance_id=instance.instance_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.task_instances[task_instance.task_instance_id] = task_instance
        instance.current_task_ids.append(task_id)
        
        # Handle different task types
        if task.task_type == TaskType.MANUAL:
            await self._create_human_task(task_instance, task)
            task_instance.status = TaskStatus.WAITING
        elif task.task_type == TaskType.TIMER:
            await self._create_timer_event(instance, task)
            task_instance.status = TaskStatus.WAITING
        else:
            # Simulate task execution
            success = random.random() > 0.1  # 90% success
            
            if success:
                task_instance.status = TaskStatus.COMPLETED
                task_instance.completed_at = datetime.now()
                instance.completed_task_ids.append(task_id)
                instance.current_task_ids.remove(task_id)
                
                # Move to next element
                await self._advance_to_next(instance, task_id)
            else:
                if task_instance.retry_count < task.retry_count:
                    task_instance.retry_count += 1
                    task_instance.status = TaskStatus.PENDING
                else:
                    task_instance.status = TaskStatus.FAILED
                    task_instance.error_message = "Task execution failed"
                    
    async def _process_gateway(self, instance: WorkflowInstance, gateway_id: str):
        """Обработка шлюза"""
        gateway = self.gateways.get(gateway_id)
        if not gateway:
            return
            
        workflow = self.workflows.get(instance.workflow_id)
        if not workflow:
            return
            
        # Find outgoing transitions
        outgoing = [t for t in self.transitions.values() 
                   if t.transition_id in workflow.transition_ids and t.source_id == gateway_id]
        outgoing.sort(key=lambda x: x.order)
        
        if gateway.gateway_type == GatewayType.EXCLUSIVE:
            # Take first matching condition
            for trans in outgoing:
                if trans.transition_type == TransitionType.DEFAULT or self._evaluate_condition(trans.condition_expression, instance.variables):
                    await self._process_element(instance, trans.target_id)
                    break
        elif gateway.gateway_type == GatewayType.PARALLEL:
            # Take all paths
            for trans in outgoing:
                await self._process_element(instance, trans.target_id)
        elif gateway.gateway_type == GatewayType.INCLUSIVE:
            # Take all matching paths
            for trans in outgoing:
                if trans.transition_type == TransitionType.DEFAULT or self._evaluate_condition(trans.condition_expression, instance.variables):
                    await self._process_element(instance, trans.target_id)
                    
    async def _process_event(self, instance: WorkflowInstance, event_id: str):
        """Обработка события"""
        event = self.events.get(event_id)
        if not event:
            return
            
        if event.event_type == EventType.START:
            # Start event - advance to first task
            await self._advance_to_next(instance, event_id)
        elif event.event_type == EventType.END:
            # End event - complete instance
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.now()
        elif event.event_type == EventType.TIMER:
            # Create timer
            await self._create_timer_for_event(instance, event)
            
    async def _advance_to_next(self, instance: WorkflowInstance, element_id: str):
        """Переход к следующему элементу"""
        workflow = self.workflows.get(instance.workflow_id)
        if not workflow:
            return
            
        # Find outgoing transitions
        for trans_id in workflow.transition_ids:
            trans = self.transitions.get(trans_id)
            if trans and trans.source_id == element_id:
                await self._process_element(instance, trans.target_id)
                
    def _evaluate_condition(self, expression: str, variables: Dict[str, Any]) -> bool:
        """Вычисление условия"""
        if not expression:
            return True
        # Simple evaluation (in real implementation would use expression language)
        try:
            return eval(expression, {"__builtins__": {}}, variables)
        except:
            return False
            
    async def _create_human_task(self, task_instance: TaskInstance, task: TaskDefinition):
        """Создание человеческой задачи"""
        human_task = HumanTask(
            human_task_id=f"ht_{uuid.uuid4().hex[:8]}",
            task_instance_id=task_instance.task_instance_id,
            assignee=task.assignee,
            candidate_groups=task.candidate_groups.copy(),
            priority=50
        )
        
        self.human_tasks[human_task.human_task_id] = human_task
        
    async def _create_timer_event(self, instance: WorkflowInstance, task: TaskDefinition):
        """Создание таймерного события"""
        timer = TimerEvent(
            timer_id=f"timer_{uuid.uuid4().hex[:8]}",
            event_id="",
            instance_id=instance.instance_id,
            timer_type="duration",
            timer_definition=task.parameters.get("duration", "PT1H"),
            fire_time=datetime.now() + timedelta(hours=1)
        )
        
        self.timer_events[timer.timer_id] = timer
        
    async def _create_timer_for_event(self, instance: WorkflowInstance, event: Event):
        """Создание таймера для события"""
        timer = TimerEvent(
            timer_id=f"timer_{uuid.uuid4().hex[:8]}",
            event_id=event.event_id,
            instance_id=instance.instance_id,
            timer_type=event.trigger_config.get("type", "duration"),
            timer_definition=event.trigger_config.get("definition", "PT1H")
        )
        
        self.timer_events[timer.timer_id] = timer
        
    async def _record_history(self, instance_id: str, event_type: str, element_id: str):
        """Запись истории"""
        history = ProcessHistory(
            history_id=f"hist_{uuid.uuid4().hex[:8]}",
            instance_id=instance_id,
            event_type=event_type,
            element_id=element_id
        )
        
        self.history[history.history_id] = history
        
    async def complete_human_task(self, human_task_id: str,
                                 user_id: str,
                                 output_data: Dict[str, Any] = None) -> bool:
        """Завершение человеческой задачи"""
        human_task = self.human_tasks.get(human_task_id)
        if not human_task or human_task.status == HumanTaskStatus.COMPLETED:
            return False
            
        human_task.status = HumanTaskStatus.COMPLETED
        human_task.completed_at = datetime.now()
        
        task_instance = self.task_instances.get(human_task.task_instance_id)
        if task_instance:
            task_instance.status = TaskStatus.COMPLETED
            task_instance.completed_at = datetime.now()
            task_instance.output_data = output_data or {}
            
            instance = self.instances.get(task_instance.instance_id)
            if instance:
                if task_instance.task_id in instance.current_task_ids:
                    instance.current_task_ids.remove(task_instance.task_id)
                instance.completed_task_ids.append(task_instance.task_id)
                
                # Advance to next
                await self._advance_to_next(instance, task_instance.task_id)
                
        return True
        
    async def claim_human_task(self, human_task_id: str, user_id: str) -> bool:
        """Принятие человеческой задачи"""
        human_task = self.human_tasks.get(human_task_id)
        if not human_task or human_task.status != HumanTaskStatus.CREATED:
            return False
            
        human_task.status = HumanTaskStatus.CLAIMED
        human_task.assignee = user_id
        human_task.claimed_at = datetime.now()
        
        return True
        
    async def cancel_instance(self, instance_id: str, reason: str = "") -> bool:
        """Отмена экземпляра"""
        instance = self.instances.get(instance_id)
        if not instance or instance.status not in [WorkflowStatus.ACTIVE]:
            return False
            
        instance.status = WorkflowStatus.CANCELLED
        instance.completed_at = datetime.now()
        
        # Cancel running tasks
        for ti in self.task_instances.values():
            if ti.instance_id == instance_id and ti.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.WAITING]:
                ti.status = TaskStatus.CANCELLED
                
        return True
        
    async def collect_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """Сбор метрик"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
            
        workflow_instances = [i for i in self.instances.values() if i.workflow_id == workflow_id]
        
        metrics = WorkflowMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            workflow_id=workflow_id,
            total_instances=len(workflow_instances),
            active_instances=sum(1 for i in workflow_instances if i.status == WorkflowStatus.ACTIVE),
            completed_instances=sum(1 for i in workflow_instances if i.status == WorkflowStatus.COMPLETED),
            failed_instances=sum(1 for i in workflow_instances if i.status == WorkflowStatus.FAILED)
        )
        
        # Calculate durations
        completed = [i for i in workflow_instances if i.completed_at]
        if completed:
            durations = [(i.completed_at - i.started_at).total_seconds() for i in completed]
            metrics.avg_duration_seconds = sum(durations) / len(durations)
            metrics.min_duration_seconds = min(durations)
            metrics.max_duration_seconds = max(durations)
            
        # Tasks per instance
        if workflow_instances:
            metrics.avg_tasks_per_instance = sum(len(i.completed_task_ids) for i in workflow_instances) / len(workflow_instances)
            
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_workflows = len(self.workflows)
        active_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE)
        
        total_instances = len(self.instances)
        active_instances = sum(1 for i in self.instances.values() if i.status == WorkflowStatus.ACTIVE)
        completed_instances = sum(1 for i in self.instances.values() if i.status == WorkflowStatus.COMPLETED)
        
        total_tasks = len(self.tasks)
        total_task_instances = len(self.task_instances)
        running_tasks = sum(1 for t in self.task_instances.values() if t.status == TaskStatus.RUNNING)
        
        total_human_tasks = len(self.human_tasks)
        pending_human_tasks = sum(1 for h in self.human_tasks.values() if h.status in [HumanTaskStatus.CREATED, HumanTaskStatus.CLAIMED])
        
        total_timers = len(self.timer_events)
        pending_timers = sum(1 for t in self.timer_events.values() if not t.is_fired)
        
        return {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "total_instances": total_instances,
            "active_instances": active_instances,
            "completed_instances": completed_instances,
            "total_tasks": total_tasks,
            "total_task_instances": total_task_instances,
            "running_tasks": running_tasks,
            "total_human_tasks": total_human_tasks,
            "pending_human_tasks": pending_human_tasks,
            "total_timers": total_timers,
            "pending_timers": pending_timers
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 347: Workflow Engine Platform")
    print("=" * 60)
    
    engine = WorkflowEngine()
    print("✓ Workflow Engine initialized")
    
    # Create Workflows
    print("\n📋 Creating Workflow Definitions...")
    
    workflows_data = [
        ("Order Processing", "Process customer orders end-to-end", "sales", ["order", "ecommerce"]),
        ("Employee Onboarding", "New employee onboarding workflow", "hr", ["hr", "onboarding"]),
        ("Invoice Approval", "Multi-level invoice approval", "finance", ["finance", "approval"]),
        ("IT Service Request", "IT service desk workflow", "it", ["it", "support"]),
        ("Leave Request", "Employee leave approval workflow", "hr", ["hr", "leave"])
    ]
    
    workflows = []
    for name, desc, cat, tags in workflows_data:
        wf = await engine.create_workflow(name, desc, cat, tags, 86400)
        workflows.append(wf)
        print(f"  📋 {name} ({cat})")
        
    # Add Tasks to first workflow (Order Processing)
    print("\n🔧 Adding Tasks to Order Processing workflow...")
    
    order_wf = workflows[0]
    
    tasks_data = [
        ("Validate Order", TaskType.SERVICE, "order-validation-service", {"validate_inventory": True}),
        ("Check Inventory", TaskType.SERVICE, "inventory-service", {"reserve": True}),
        ("Process Payment", TaskType.SERVICE, "payment-service", {"gateway": "stripe"}),
        ("Create Shipment", TaskType.SERVICE, "shipping-service", {"carrier": "auto"}),
        ("Send Notification", TaskType.SERVICE, "notification-service", {"channels": ["email", "sms"]}),
        ("Manual Review", TaskType.MANUAL, "", {}, "", ["order-reviewers"]),
        ("Wait for Payment", TaskType.TIMER, "", {"duration": "PT24H"})
    ]
    
    tasks = []
    for name, ttype, impl, params, *rest in tasks_data:
        assignee = rest[0] if len(rest) > 0 else ""
        groups = rest[1] if len(rest) > 1 else []
        t = await engine.add_task(order_wf.workflow_id, name, ttype, impl, params, 300, 3, assignee, groups)
        if t:
            tasks.append(t)
            print(f"  🔧 {name} ({ttype.value})")
            
    # Add Gateways
    print("\n🚦 Adding Gateways...")
    
    gateways_data = [
        ("Order Valid?", GatewayType.EXCLUSIVE),
        ("Inventory Available?", GatewayType.EXCLUSIVE),
        ("Payment Type", GatewayType.EXCLUSIVE),
        ("Parallel Tasks", GatewayType.PARALLEL),
        ("Join Parallel", GatewayType.PARALLEL)
    ]
    
    gateways = []
    for name, gtype in gateways_data:
        g = await engine.add_gateway(order_wf.workflow_id, name, gtype)
        if g:
            gateways.append(g)
            print(f"  🚦 {name} ({gtype.value})")
            
    # Add Events
    print("\n🎯 Adding Events...")
    
    events_data = [
        ("Order Received", EventType.START, "message", {"message_ref": "order_message"}),
        ("Order Completed", EventType.END, "", {}),
        ("Order Cancelled", EventType.END, "", {}),
        ("Payment Timeout", EventType.TIMER, "timer", {"type": "duration", "definition": "PT24H"}),
        ("Cancellation Request", EventType.BOUNDARY, "message", {"message_ref": "cancel_message"})
    ]
    
    events = []
    for name, etype, trigger, config in events_data:
        e = await engine.add_event(order_wf.workflow_id, name, etype, trigger, config)
        if e:
            events.append(e)
            print(f"  🎯 {name} ({etype.value})")
            
    # Add Transitions
    print("\n➡️ Adding Transitions...")
    
    # Connect elements (simplified)
    transitions = []
    
    # Start -> Validate
    t = await engine.add_transition(order_wf.workflow_id, events[0].event_id, tasks[0].task_id)
    if t:
        transitions.append(t)
        
    # Validate -> Gateway
    t = await engine.add_transition(order_wf.workflow_id, tasks[0].task_id, gateways[0].gateway_id)
    if t:
        transitions.append(t)
        
    # Gateway -> Check Inventory (valid)
    t = await engine.add_transition(order_wf.workflow_id, gateways[0].gateway_id, tasks[1].task_id, "Valid", TransitionType.CONDITIONAL, "is_valid == True")
    if t:
        transitions.append(t)
        
    # Gateway -> End (invalid)
    t = await engine.add_transition(order_wf.workflow_id, gateways[0].gateway_id, events[2].event_id, "Invalid", TransitionType.CONDITIONAL, "is_valid == False")
    if t:
        transitions.append(t)
        
    print(f"  ➡️ Created {len(transitions)} transitions")
    
    # Activate Workflows
    print("\n✅ Activating Workflows...")
    
    for wf in workflows:
        await engine.activate_workflow(wf.workflow_id)
        print(f"  ✅ {wf.name}")
        
    # Start Workflow Instances
    print("\n▶️ Starting Workflow Instances...")
    
    instances = []
    
    # Order instances
    for i in range(5):
        inst = await engine.start_instance(
            order_wf.workflow_id,
            {"order_id": f"ORD-{i+1:05d}", "customer_id": f"CUST-{random.randint(1, 100):05d}", "total": random.uniform(50, 500), "is_valid": True},
            f"user_{random.randint(1, 10)}",
            f"ORD-{i+1:05d}"
        )
        if inst:
            instances.append(inst)
            
    # Onboarding instances
    for i in range(3):
        inst = await engine.start_instance(
            workflows[1].workflow_id,
            {"employee_id": f"EMP-{i+1:05d}", "department": random.choice(["Engineering", "Sales", "Marketing"])},
            "hr_admin",
            f"ONBOARD-{i+1:05d}"
        )
        if inst:
            instances.append(inst)
            
    print(f"  ▶️ Started {len(instances)} workflow instances")
    
    # Process Human Tasks
    print("\n👤 Processing Human Tasks...")
    
    claimed = 0
    completed = 0
    
    for ht in list(engine.human_tasks.values())[:5]:
        if ht.status == HumanTaskStatus.CREATED:
            await engine.claim_human_task(ht.human_task_id, f"user_{random.randint(1, 10)}")
            claimed += 1
            
        if ht.status == HumanTaskStatus.CLAIMED and random.random() > 0.3:
            await engine.complete_human_task(ht.human_task_id, ht.assignee, {"approved": True})
            completed += 1
            
    print(f"  👤 Claimed: {claimed}, Completed: {completed}")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for wf in workflows[:3]:
        m = await engine.collect_metrics(wf.workflow_id)
        if m:
            metrics.append(m)
            print(f"  📊 {wf.name}: {m.active_instances} active, {m.completed_instances} completed")
            
    # Workflow Definitions Dashboard
    print("\n📋 Workflow Definitions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                       │ Category    │ Version │ Status    │ Tasks │ Gateways │ Events │ Transitions │ Tags                                                                                                           │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for wf in workflows:
        name = wf.name[:26].ljust(26)
        cat = wf.category[:11].ljust(11)
        version = f"v{wf.version}".ljust(7)
        
        status_icons = {"draft": "⚪", "active": "🟢", "suspended": "🟡", "completed": "✅", "failed": "🔴"}
        status_icon = status_icons.get(wf.status.value, "?")
        status = f"{status_icon} {wf.status.value}"[:9].ljust(9)
        
        tasks_cnt = str(len(wf.task_ids)).ljust(5)
        gw_cnt = str(len(wf.gateway_ids)).ljust(8)
        evt_cnt = str(len(wf.event_ids)).ljust(6)
        trans_cnt = str(len(wf.transition_ids)).ljust(11)
        tags = ", ".join(wf.tags)[:109]
        tags = tags.ljust(109)
        
        print(f"  │ {name} │ {cat} │ {version} │ {status} │ {tasks_cnt} │ {gw_cnt} │ {evt_cnt} │ {trans_cnt} │ {tags} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Task Definitions
    print("\n🔧 Task Definitions:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                    │ Type       │ Implementation               │ Timeout │ Retries │ Multi-Instance │ Assignee         │ Candidate Groups                                                                                                    │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for task in tasks:
        name = task.name[:23].ljust(23)
        ttype = task.task_type.value[:10].ljust(10)
        impl = task.implementation[:28] if task.implementation else "N/A"
        impl = impl.ljust(28)
        timeout = f"{task.timeout_seconds}s".ljust(7)
        retries = str(task.retry_count).ljust(7)
        multi = "Yes" if task.is_multi_instance else "No"
        multi = multi.ljust(14)
        assignee = task.assignee[:16] if task.assignee else "N/A"
        assignee = assignee.ljust(16)
        groups = ", ".join(task.candidate_groups)[:117] if task.candidate_groups else "N/A"
        groups = groups.ljust(117)
        
        print(f"  │ {name} │ {ttype} │ {impl} │ {timeout} │ {retries} │ {multi} │ {assignee} │ {groups} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Workflow Instances
    print("\n▶️ Workflow Instances:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Instance ID               │ Workflow                   │ Status     │ Business Key      │ Current Tasks │ Completed │ Initiator     │ Started                                                              │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for inst in instances[:10]:
        inst_id = inst.instance_id[:25].ljust(25)
        
        wf = engine.workflows.get(inst.workflow_id)
        wf_name = wf.name if wf else "Unknown"
        wf_name = wf_name[:26].ljust(26)
        
        status_icons = {"draft": "⚪", "active": "🟢", "suspended": "🟡", "completed": "✅", "failed": "🔴", "cancelled": "⚫"}
        status_icon = status_icons.get(inst.status.value, "?")
        status = f"{status_icon} {inst.status.value}"[:10].ljust(10)
        
        bkey = inst.business_key[:17] if inst.business_key else "N/A"
        bkey = bkey.ljust(17)
        
        current = str(len(inst.current_task_ids)).ljust(13)
        completed = str(len(inst.completed_task_ids)).ljust(9)
        initiator = inst.initiator[:13] if inst.initiator else "N/A"
        initiator = initiator.ljust(13)
        started = inst.started_at.strftime("%Y-%m-%d %H:%M:%S")[:70].ljust(70)
        
        print(f"  │ {inst_id} │ {wf_name} │ {status} │ {bkey} │ {current} │ {completed} │ {initiator} │ {started} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Human Tasks
    print("\n👤 Human Tasks:")
    
    human_tasks = list(engine.human_tasks.values())[:8]
    if human_tasks:
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Task ID               │ Status       │ Priority │ Assignee          │ Candidate Groups           │ Created              │ Claimed              │ Due Date                                       │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for ht in human_tasks:
            task_id = ht.human_task_id[:21].ljust(21)
            
            status_icons = {"created": "⚪", "claimed": "🟡", "in_progress": "🔵", "completed": "✅", "delegated": "↗️", "escalated": "🔴"}
            status_icon = status_icons.get(ht.status.value, "?")
            status = f"{status_icon} {ht.status.value}"[:12].ljust(12)
            
            priority = str(ht.priority).ljust(8)
            assignee = ht.assignee[:17] if ht.assignee else "Unassigned"
            assignee = assignee.ljust(17)
            groups = ", ".join(ht.candidate_groups)[:26] if ht.candidate_groups else "N/A"
            groups = groups.ljust(26)
            
            created = ht.created_at.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
            claimed = ht.claimed_at.strftime("%Y-%m-%d %H:%M:%S") if ht.claimed_at else "N/A"
            claimed = claimed[:20].ljust(20)
            due = ht.due_date.strftime("%Y-%m-%d %H:%M:%S") if ht.due_date else "N/A"
            due = due[:48].ljust(48)
            
            print(f"  │ {task_id} │ {status} │ {priority} │ {assignee} │ {groups} │ {created} │ {claimed} │ {due} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print("  No human tasks")
        
    # Workflow Metrics
    print("\n📊 Workflow Metrics:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Workflow                   │ Total Instances │ Active │ Completed │ Failed │ Avg Duration │ Min Duration │ Max Duration │ Avg Tasks/Instance                                                                                                   │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in metrics:
        wf = engine.workflows.get(m.workflow_id)
        wf_name = wf.name if wf else "Unknown"
        wf_name = wf_name[:26].ljust(26)
        
        total = str(m.total_instances).ljust(15)
        active = str(m.active_instances).ljust(6)
        completed = str(m.completed_instances).ljust(9)
        failed = str(m.failed_instances).ljust(6)
        avg_dur = f"{m.avg_duration_seconds:.0f}s".ljust(12)
        min_dur = f"{m.min_duration_seconds:.0f}s".ljust(12)
        max_dur = f"{m.max_duration_seconds:.0f}s".ljust(12)
        avg_tasks = f"{m.avg_tasks_per_instance:.1f}".ljust(115)
        
        print(f"  │ {wf_name} │ {total} │ {active} │ {completed} │ {failed} │ {avg_dur} │ {min_dur} │ {max_dur} │ {avg_tasks} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = engine.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Workflows: {stats['active_workflows']}/{stats['total_workflows']} active")
    print(f"  Instances: {stats['active_instances']} active, {stats['completed_instances']} completed")
    print(f"  Tasks: {stats['total_tasks']} definitions, {stats['running_tasks']} running")
    print(f"  Human Tasks: {stats['pending_human_tasks']} pending")
    print(f"  Timers: {stats['pending_timers']} pending")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Workflow Engine Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Workflows:             {stats['active_workflows']:>12}                      │")
    print(f"│ Total Instances:              {stats['total_instances']:>12}                      │")
    print(f"│ Active Instances:             {stats['active_instances']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Task Definitions:             {stats['total_tasks']:>12}                      │")
    print(f"│ Running Tasks:                {stats['running_tasks']:>12}                      │")
    print(f"│ Pending Human Tasks:          {stats['pending_human_tasks']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Workflow Engine Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
