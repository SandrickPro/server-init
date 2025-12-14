#!/usr/bin/env python3
"""
Server Init - Iteration 252: Saga Orchestrator Platform
Платформа оркестрации распределённых транзакций

Функционал:
- Saga Definition - определение саг
- Step Orchestration - оркестрация шагов
- Compensation Handling - обработка компенсаций
- State Management - управление состоянием
- Timeout Handling - обработка таймаутов
- Retry Logic - логика повторов
- Saga History - история выполнения
- Dead Letter Handling - обработка ошибок
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
import uuid


class SagaState(Enum):
    """Состояние саги"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class StepState(Enum):
    """Состояние шага"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    SKIPPED = "skipped"


class StepType(Enum):
    """Тип шага"""
    ACTION = "action"
    COMPENSATION = "compensation"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class TimeoutAction(Enum):
    """Действие при таймауте"""
    RETRY = "retry"
    COMPENSATE = "compensate"
    FAIL = "fail"


@dataclass
class SagaStep:
    """Шаг саги"""
    step_id: str
    name: str
    
    # Type
    step_type: StepType = StepType.ACTION
    
    # Order
    order: int = 0
    
    # State
    state: StepState = StepState.PENDING
    
    # Actions
    action: Optional[Callable[..., Awaitable[Any]]] = None
    compensation: Optional[Callable[..., Awaitable[Any]]] = None
    
    # Configuration
    timeout_ms: int = 30000
    max_retries: int = 3
    retry_delay_ms: int = 1000
    
    # Result
    result: Any = None
    error: str = ""
    
    # Attempts
    attempts: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0


@dataclass
class SagaDefinition:
    """Определение саги"""
    definition_id: str
    name: str
    description: str = ""
    
    # Steps
    steps: List[SagaStep] = field(default_factory=list)
    
    # Configuration
    timeout_ms: int = 300000  # 5 minutes
    max_retries: int = 3
    timeout_action: TimeoutAction = TimeoutAction.COMPENSATE
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Version
    version: str = "1.0.0"
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SagaInstance:
    """Экземпляр саги"""
    instance_id: str
    definition_id: str
    
    # State
    state: SagaState = SagaState.PENDING
    
    # Input/Output
    input_data: Any = None
    output_data: Any = None
    
    # Steps execution
    step_results: Dict[str, Any] = field(default_factory=dict)
    current_step: int = 0
    
    # Compensation
    compensating_from_step: int = -1
    
    # Error
    error_message: str = ""
    
    # Correlation
    correlation_id: str = ""
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SagaEvent:
    """Событие саги"""
    event_id: str
    instance_id: str
    
    # Event
    event_type: str = ""
    step_name: str = ""
    
    # Data
    data: Any = None
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CompensationRecord:
    """Запись о компенсации"""
    record_id: str
    instance_id: str
    step_name: str
    
    # Result
    success: bool = False
    error: str = ""
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class SagaOrchestrator:
    """Оркестратор саг"""
    
    def __init__(self):
        self.definitions: Dict[str, SagaDefinition] = {}
        self.instances: Dict[str, SagaInstance] = {}
        self.events: List[SagaEvent] = []
        self.compensations: List[CompensationRecord] = []
        
        # Stats
        self._total_started = 0
        self._total_completed = 0
        self._total_compensated = 0
        self._total_failed = 0
        
    def create_definition(self, name: str, description: str = "",
                         timeout_ms: int = 300000) -> SagaDefinition:
        """Создание определения саги"""
        definition = SagaDefinition(
            definition_id=f"def_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            timeout_ms=timeout_ms
        )
        
        self.definitions[definition.definition_id] = definition
        return definition
        
    def add_step(self, definition_id: str, name: str,
                action: Callable[..., Awaitable[Any]],
                compensation: Callable[..., Awaitable[Any]] = None,
                timeout_ms: int = 30000,
                max_retries: int = 3) -> Optional[SagaStep]:
        """Добавление шага к определению"""
        definition = self.definitions.get(definition_id)
        if not definition:
            return None
            
        step = SagaStep(
            step_id=f"step_{uuid.uuid4().hex[:8]}",
            name=name,
            order=len(definition.steps),
            action=action,
            compensation=compensation,
            timeout_ms=timeout_ms,
            max_retries=max_retries
        )
        
        definition.steps.append(step)
        return step
        
    async def start(self, definition_name: str, input_data: Any = None,
                   correlation_id: str = "") -> Optional[SagaInstance]:
        """Запуск экземпляра саги"""
        # Find definition
        definition = None
        for d in self.definitions.values():
            if d.name == definition_name:
                definition = d
                break
                
        if not definition:
            return None
            
        # Create instance
        instance = SagaInstance(
            instance_id=f"saga_{uuid.uuid4().hex[:8]}",
            definition_id=definition.definition_id,
            input_data=input_data,
            correlation_id=correlation_id or str(uuid.uuid4()),
            started_at=datetime.now()
        )
        
        self.instances[instance.instance_id] = instance
        self._total_started += 1
        
        # Record event
        self._record_event(instance.instance_id, "saga_started", "", input_data)
        
        # Execute saga
        await self._execute_saga(instance, definition)
        
        return instance
        
    async def _execute_saga(self, instance: SagaInstance,
                           definition: SagaDefinition):
        """Выполнение саги"""
        instance.state = SagaState.RUNNING
        
        for i, step_template in enumerate(definition.steps):
            instance.current_step = i
            
            # Create step instance
            step = SagaStep(
                step_id=step_template.step_id,
                name=step_template.name,
                order=step_template.order,
                action=step_template.action,
                compensation=step_template.compensation,
                timeout_ms=step_template.timeout_ms,
                max_retries=step_template.max_retries,
                retry_delay_ms=step_template.retry_delay_ms
            )
            
            # Execute step
            success = await self._execute_step(instance, step)
            
            if not success:
                # Start compensation
                instance.compensating_from_step = i - 1
                await self._compensate(instance, definition)
                return
                
            instance.step_results[step.name] = step.result
            
        # Saga completed
        instance.state = SagaState.COMPLETED
        instance.completed_at = datetime.now()
        instance.duration_ms = (instance.completed_at - instance.started_at).total_seconds() * 1000
        instance.output_data = instance.step_results
        
        self._total_completed += 1
        self._record_event(instance.instance_id, "saga_completed", "", instance.output_data)
        
    async def _execute_step(self, instance: SagaInstance,
                           step: SagaStep) -> bool:
        """Выполнение шага"""
        step.state = StepState.RUNNING
        step.started_at = datetime.now()
        
        self._record_event(instance.instance_id, "step_started", step.name, None)
        
        for attempt in range(step.max_retries + 1):
            step.attempts = attempt + 1
            
            try:
                if step.action:
                    # Simulate action execution
                    await asyncio.sleep(random.uniform(0.01, 0.1))
                    
                    # Simulate success/failure
                    if random.random() < 0.85:
                        step.result = {
                            "step": step.name,
                            "status": "success",
                            "attempt": attempt + 1,
                            "input": instance.input_data
                        }
                        step.state = StepState.COMPLETED
                        step.completed_at = datetime.now()
                        step.duration_ms = (step.completed_at - step.started_at).total_seconds() * 1000
                        
                        self._record_event(
                            instance.instance_id, "step_completed",
                            step.name, step.result
                        )
                        return True
                    else:
                        raise Exception(f"Step {step.name} failed (simulated)")
                        
            except Exception as e:
                step.error = str(e)
                
                if attempt < step.max_retries:
                    self._record_event(
                        instance.instance_id, "step_retry",
                        step.name, {"attempt": attempt + 1, "error": str(e)}
                    )
                    await asyncio.sleep(step.retry_delay_ms / 1000)
                else:
                    step.state = StepState.FAILED
                    step.completed_at = datetime.now()
                    
                    self._record_event(
                        instance.instance_id, "step_failed",
                        step.name, {"error": str(e), "attempts": step.attempts}
                    )
                    
                    instance.error_message = str(e)
                    return False
                    
        return False
        
    async def _compensate(self, instance: SagaInstance,
                         definition: SagaDefinition):
        """Выполнение компенсации"""
        instance.state = SagaState.COMPENSATING
        
        self._record_event(
            instance.instance_id, "compensation_started",
            "", {"from_step": instance.compensating_from_step}
        )
        
        # Compensate in reverse order
        for i in range(instance.compensating_from_step, -1, -1):
            step_template = definition.steps[i]
            
            if not step_template.compensation:
                continue
                
            record = CompensationRecord(
                record_id=f"comp_{uuid.uuid4().hex[:8]}",
                instance_id=instance.instance_id,
                step_name=step_template.name,
                started_at=datetime.now()
            )
            
            try:
                await asyncio.sleep(random.uniform(0.01, 0.05))
                record.success = True
                
                self._record_event(
                    instance.instance_id, "step_compensated",
                    step_template.name, None
                )
                
            except Exception as e:
                record.success = False
                record.error = str(e)
                
            record.completed_at = datetime.now()
            self.compensations.append(record)
            
        instance.state = SagaState.COMPENSATED
        instance.completed_at = datetime.now()
        instance.duration_ms = (instance.completed_at - instance.started_at).total_seconds() * 1000
        
        self._total_compensated += 1
        self._record_event(instance.instance_id, "saga_compensated", "", None)
        
    def _record_event(self, instance_id: str, event_type: str,
                     step_name: str, data: Any):
        """Запись события"""
        event = SagaEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            instance_id=instance_id,
            event_type=event_type,
            step_name=step_name,
            data=data
        )
        
        self.events.append(event)
        
    def get_instance(self, instance_id: str) -> Optional[SagaInstance]:
        """Получение экземпляра саги"""
        return self.instances.get(instance_id)
        
    def get_instance_events(self, instance_id: str) -> List[SagaEvent]:
        """Получение событий экземпляра"""
        return [e for e in self.events if e.instance_id == instance_id]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        running = sum(1 for i in self.instances.values() if i.state == SagaState.RUNNING)
        
        durations = [i.duration_ms for i in self.instances.values() if i.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        success_rate = (self._total_completed / self._total_started * 100) if self._total_started > 0 else 0
        
        return {
            "definitions_total": len(self.definitions),
            "instances_total": len(self.instances),
            "instances_running": running,
            "total_started": self._total_started,
            "total_completed": self._total_completed,
            "total_compensated": self._total_compensated,
            "total_failed": self._total_failed,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "total_events": len(self.events),
            "total_compensations": len(self.compensations)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 252: Saga Orchestrator Platform")
    print("=" * 60)
    
    orchestrator = SagaOrchestrator()
    print("✓ Saga Orchestrator created")
    
    # Define step actions (simulated)
    async def create_order(ctx): return {"order_id": "O001"}
    async def reserve_inventory(ctx): return {"reserved": True}
    async def charge_payment(ctx): return {"payment_id": "P001"}
    async def ship_order(ctx): return {"tracking": "TRK123"}
    async def send_notification(ctx): return {"sent": True}
    
    # Define compensations
    async def cancel_order(ctx): return {"cancelled": True}
    async def release_inventory(ctx): return {"released": True}
    async def refund_payment(ctx): return {"refunded": True}
    async def cancel_shipment(ctx): return {"cancelled": True}
    
    # Create saga definitions
    print("\n📋 Creating Saga Definitions...")
    
    # Order Fulfillment Saga
    order_saga = orchestrator.create_definition(
        "OrderFulfillment",
        "Complete order fulfillment process",
        timeout_ms=300000
    )
    
    steps_config = [
        ("CreateOrder", create_order, cancel_order),
        ("ReserveInventory", reserve_inventory, release_inventory),
        ("ChargePayment", charge_payment, refund_payment),
        ("ShipOrder", ship_order, cancel_shipment),
        ("SendNotification", send_notification, None),
    ]
    
    for name, action, compensation in steps_config:
        orchestrator.add_step(order_saga.definition_id, name, action, compensation)
        
    print(f"  📋 {order_saga.name} ({len(order_saga.steps)} steps)")
    
    # User Registration Saga
    user_saga = orchestrator.create_definition(
        "UserRegistration",
        "Complete user registration process",
        timeout_ms=60000
    )
    
    async def create_user(ctx): return {"user_id": "U001"}
    async def setup_profile(ctx): return {"profile": True}
    async def send_welcome(ctx): return {"sent": True}
    
    async def delete_user(ctx): return {"deleted": True}
    async def cleanup_profile(ctx): return {"cleaned": True}
    
    reg_steps = [
        ("CreateUser", create_user, delete_user),
        ("SetupProfile", setup_profile, cleanup_profile),
        ("SendWelcomeEmail", send_welcome, None),
    ]
    
    for name, action, compensation in reg_steps:
        orchestrator.add_step(user_saga.definition_id, name, action, compensation)
        
    print(f"  📋 {user_saga.name} ({len(user_saga.steps)} steps)")
    
    # Execute sagas
    print("\n🚀 Executing Sagas...")
    
    # Execute multiple order sagas
    sagas = []
    for i in range(5):
        instance = await orchestrator.start(
            "OrderFulfillment",
            {"order_id": f"ORD-{1000 + i}", "amount": 99.99 + i * 10}
        )
        if instance:
            sagas.append(instance)
            status_icon = {
                SagaState.COMPLETED: "✓",
                SagaState.COMPENSATED: "↩",
                SagaState.FAILED: "✗"
            }.get(instance.state, "?")
            print(f"  {status_icon} Order Saga {i+1}: {instance.state.value} ({instance.duration_ms:.0f}ms)")
            
    # Execute user registration sagas
    for i in range(3):
        instance = await orchestrator.start(
            "UserRegistration",
            {"email": f"user{i+1}@example.com"}
        )
        if instance:
            sagas.append(instance)
            status_icon = "✓" if instance.state == SagaState.COMPLETED else "✗"
            print(f"  {status_icon} User Saga {i+1}: {instance.state.value} ({instance.duration_ms:.0f}ms)")
            
    # Display definitions
    print("\n📋 Saga Definitions:")
    
    print("\n  ┌─────────────────────┬──────────┬────────────┬──────────────────┐")
    print("  │ Definition          │ Steps    │ Timeout    │ Version          │")
    print("  ├─────────────────────┼──────────┼────────────┼──────────────────┤")
    
    for definition in orchestrator.definitions.values():
        name = definition.name[:19].ljust(19)
        steps = str(len(definition.steps))[:8].ljust(8)
        timeout = f"{definition.timeout_ms/1000:.0f}s"[:10].ljust(10)
        version = definition.version[:16].ljust(16)
        
        print(f"  │ {name} │ {steps} │ {timeout} │ {version} │")
        
    print("  └─────────────────────┴──────────┴────────────┴──────────────────┘")
    
    # Display steps for Order saga
    print("\n📌 Steps (OrderFulfillment):")
    
    print("\n  ┌───────┬─────────────────────┬────────────┬───────────┬──────────┐")
    print("  │ Order │ Step                │ Timeout    │ Retries   │ Comp.    │")
    print("  ├───────┼─────────────────────┼────────────┼───────────┼──────────┤")
    
    for step in order_saga.steps:
        order_num = str(step.order)[:5].ljust(5)
        name = step.name[:19].ljust(19)
        timeout = f"{step.timeout_ms/1000:.0f}s"[:10].ljust(10)
        retries = str(step.max_retries)[:9].ljust(9)
        has_comp = "✓" if step.compensation else "-"
        
        print(f"  │ {order_num} │ {name} │ {timeout} │ {retries} │ {has_comp:8s} │")
        
    print("  └───────┴─────────────────────┴────────────┴───────────┴──────────┘")
    
    # Display instances
    print("\n🔄 Saga Instances:")
    
    print("\n  ┌──────────────────┬─────────────────┬───────────────┬──────────────┐")
    print("  │ Instance         │ Definition      │ State         │ Duration     │")
    print("  ├──────────────────┼─────────────────┼───────────────┼──────────────┤")
    
    for instance in list(orchestrator.instances.values())[:8]:
        inst_id = instance.instance_id[:16].ljust(16)
        
        definition = orchestrator.definitions.get(instance.definition_id)
        def_name = (definition.name if definition else "?")[:15].ljust(15)
        
        state = instance.state.value[:13].ljust(13)
        duration = f"{instance.duration_ms:.0f}ms"[:12].ljust(12)
        
        print(f"  │ {inst_id} │ {def_name} │ {state} │ {duration} │")
        
    print("  └──────────────────┴─────────────────┴───────────────┴──────────────┘")
    
    # Display events for first saga
    if sagas:
        print(f"\n📜 Events for {sagas[0].instance_id}:")
        
        events = orchestrator.get_instance_events(sagas[0].instance_id)
        for event in events[:8]:
            step_info = f" ({event.step_name})" if event.step_name else ""
            print(f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.event_type}{step_info}")
            
    # State distribution
    print("\n📊 Saga State Distribution:")
    
    state_counts: Dict[SagaState, int] = {}
    for instance in orchestrator.instances.values():
        state_counts[instance.state] = state_counts.get(instance.state, 0) + 1
        
    for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count + "░" * (10 - count)
        icon = {
            SagaState.COMPLETED: "✓",
            SagaState.COMPENSATED: "↩",
            SagaState.FAILED: "✗",
            SagaState.RUNNING: "→"
        }.get(state, "?")
        print(f"  {icon} {state.value:15s} [{bar}] {count}")
        
    # Compensations
    print(f"\n↩ Compensation Records: {len(orchestrator.compensations)}")
    
    for comp in orchestrator.compensations[:5]:
        status = "✓" if comp.success else "✗"
        print(f"  {status} {comp.step_name} ({comp.instance_id[:12]}...)")
        
    # Statistics
    print("\n📊 Orchestrator Statistics:")
    
    stats = orchestrator.get_statistics()
    
    print(f"\n  Definitions: {stats['definitions_total']}")
    print(f"  Instances: {stats['instances_total']} (running: {stats['instances_running']})")
    
    print(f"\n  Started: {stats['total_started']}")
    print(f"  Completed: {stats['total_completed']}")
    print(f"  Compensated: {stats['total_compensated']}")
    print(f"  Failed: {stats['total_failed']}")
    
    print(f"\n  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Avg Duration: {stats['avg_duration_ms']:.0f}ms")
    
    print(f"\n  Events: {stats['total_events']}")
    print(f"  Compensations: {stats['total_compensations']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Saga Orchestrator Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Definitions:                   {stats['definitions_total']:>12}                        │")
    print(f"│ Instances:                     {stats['instances_total']:>12}                        │")
    print(f"│ Running:                       {stats['instances_running']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                  {stats['success_rate']:>11.1f}%                        │")
    print(f"│ Avg Duration:                  {stats['avg_duration_ms']:>10.0f}ms                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Saga Orchestrator Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
