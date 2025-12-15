#!/usr/bin/env python3
"""
Server Init - Iteration 350: Batch Processing Platform
Платформа пакетной обработки

Функционал:
- Batch Jobs - пакетные задания
- Job Steps - шаги заданий
- Chunk Processing - обработка чанками
- Item Processing - обработка элементов
- Job Parameters - параметры заданий
- Restart/Recovery - перезапуск и восстановление
- Partitioning - партиционирование
- Job Repository - репозиторий заданий
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json


class BatchStatus(Enum):
    """Статус пакета"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class StepStatus(Enum):
    """Статус шага"""
    UNKNOWN = "unknown"
    STARTING = "starting"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class StepType(Enum):
    """Тип шага"""
    TASKLET = "tasklet"
    CHUNK = "chunk"
    PARTITION = "partition"
    FLOW = "flow"


class ExitStatus(Enum):
    """Статус выхода"""
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    NOOP = "noop"
    UNKNOWN = "unknown"


class RestartPolicy(Enum):
    """Политика перезапуска"""
    NEVER = "never"
    ALWAYS = "always"
    ON_FAILURE = "on_failure"


class PartitionStrategy(Enum):
    """Стратегия партиционирования"""
    RANGE = "range"
    HASH = "hash"
    ROUND_ROBIN = "round_robin"
    CUSTOM = "custom"


@dataclass
class JobParameter:
    """Параметр задания"""
    name: str
    value: Any
    param_type: str = "string"  # string, long, double, date
    identifying: bool = True


@dataclass
class JobDefinition:
    """Определение задания"""
    job_id: str
    name: str
    
    # Steps
    step_names: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: Dict[str, JobParameter] = field(default_factory=dict)
    
    # Configuration
    restartable: bool = True
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    
    # Listeners
    listeners: List[str] = field(default_factory=list)
    
    # Validators
    validators: List[str] = field(default_factory=list)
    
    # Description
    description: str = ""
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StepDefinition:
    """Определение шага"""
    step_id: str
    name: str
    job_id: str
    
    # Type
    step_type: StepType = StepType.CHUNK
    
    # Chunk
    chunk_size: int = 100
    commit_interval: int = 1
    
    # Reader/Processor/Writer
    reader_name: str = ""
    processor_name: str = ""
    writer_name: str = ""
    
    # Tasklet
    tasklet_name: str = ""
    
    # Skip/Retry
    skip_limit: int = 10
    retry_limit: int = 3
    skippable_exceptions: List[str] = field(default_factory=list)
    retryable_exceptions: List[str] = field(default_factory=list)
    
    # Transaction
    allow_start_if_complete: bool = False
    
    # Next
    next_step: str = ""
    
    # Flow
    flow_steps: List[str] = field(default_factory=list)
    
    # Order
    order: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobExecution:
    """Выполнение задания"""
    execution_id: str
    job_id: str
    job_instance_id: str
    
    # Status
    status: BatchStatus = BatchStatus.UNKNOWN
    exit_status: ExitStatus = ExitStatus.UNKNOWN
    
    # Parameters
    job_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Failure
    failure_exceptions: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class JobInstance:
    """Экземпляр задания"""
    instance_id: str
    job_id: str
    
    # Job Parameters (identify the instance)
    job_key: str = ""
    
    # Executions
    execution_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StepExecution:
    """Выполнение шага"""
    execution_id: str
    step_id: str
    job_execution_id: str
    
    # Status
    status: StepStatus = StepStatus.UNKNOWN
    exit_status: ExitStatus = ExitStatus.UNKNOWN
    
    # Counts
    read_count: int = 0
    write_count: int = 0
    commit_count: int = 0
    rollback_count: int = 0
    filter_count: int = 0
    skip_count: int = 0
    
    # Context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Failure
    failure_exceptions: List[str] = field(default_factory=list)
    
    # Timestamps
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class Partition:
    """Партиция"""
    partition_id: str
    step_id: str
    job_execution_id: str
    
    # Partition info
    partition_number: int = 0
    grid_size: int = 1
    
    # Range
    start_value: Any = None
    end_value: Any = None
    
    # Status
    status: StepStatus = StepStatus.UNKNOWN
    
    # Counts
    items_processed: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ChunkContext:
    """Контекст чанка"""
    context_id: str
    step_execution_id: str
    
    # Chunk info
    chunk_number: int = 0
    
    # Items
    items_in_chunk: int = 0
    items_processed: int = 0
    items_skipped: int = 0
    
    # Status
    is_complete: bool = False
    
    # Retry
    retry_count: int = 0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ItemReader:
    """Читатель элементов"""
    reader_id: str
    name: str
    
    # Type
    reader_type: str = ""  # jdbc, file, kafka, etc.
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    items_read: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ItemProcessor:
    """Процессор элементов"""
    processor_id: str
    name: str
    
    # Type
    processor_type: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    items_processed: int = 0
    items_filtered: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ItemWriter:
    """Писатель элементов"""
    writer_id: str
    name: str
    
    # Type
    writer_type: str = ""  # jdbc, file, kafka, etc.
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    items_written: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobListener:
    """Слушатель задания"""
    listener_id: str
    name: str
    
    # Type
    listener_type: str = ""  # before_job, after_job, etc.
    
    # Handler
    handler_name: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StepListener:
    """Слушатель шага"""
    listener_id: str
    name: str
    step_id: str
    
    # Type
    listener_type: str = ""  # before_step, after_step, before_chunk, etc.
    
    # Handler
    handler_name: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchMetrics:
    """Метрики пакетной обработки"""
    metrics_id: str
    job_id: str
    
    # Executions
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Duration
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    
    # Items
    total_items_processed: int = 0
    total_items_skipped: int = 0
    
    # Throughput
    avg_items_per_second: float = 0.0
    
    # Timestamps
    collected_at: datetime = field(default_factory=datetime.now)


class BatchProcessingPlatform:
    """Платформа пакетной обработки"""
    
    def __init__(self):
        self.job_definitions: Dict[str, JobDefinition] = {}
        self.step_definitions: Dict[str, StepDefinition] = {}
        self.job_instances: Dict[str, JobInstance] = {}
        self.job_executions: Dict[str, JobExecution] = {}
        self.step_executions: Dict[str, StepExecution] = {}
        self.partitions: Dict[str, Partition] = {}
        self.chunk_contexts: Dict[str, ChunkContext] = {}
        self.readers: Dict[str, ItemReader] = {}
        self.processors: Dict[str, ItemProcessor] = {}
        self.writers: Dict[str, ItemWriter] = {}
        self.job_listeners: Dict[str, JobListener] = {}
        self.step_listeners: Dict[str, StepListener] = {}
        self.metrics: Dict[str, BatchMetrics] = {}
        
    async def create_job(self, name: str,
                        description: str = "",
                        restartable: bool = True,
                        restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE,
                        parameters: Dict[str, Any] = None) -> JobDefinition:
        """Создание задания"""
        job = JobDefinition(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            restartable=restartable,
            restart_policy=restart_policy
        )
        
        # Add parameters
        if parameters:
            for param_name, param_value in parameters.items():
                job.parameters[param_name] = JobParameter(
                    name=param_name,
                    value=param_value
                )
                
        self.job_definitions[job.job_id] = job
        return job
        
    async def add_step(self, job_id: str, name: str,
                      step_type: StepType = StepType.CHUNK,
                      chunk_size: int = 100,
                      reader_name: str = "",
                      processor_name: str = "",
                      writer_name: str = "",
                      tasklet_name: str = "",
                      skip_limit: int = 10,
                      retry_limit: int = 3,
                      next_step: str = "",
                      order: int = 0) -> Optional[StepDefinition]:
        """Добавление шага"""
        job = self.job_definitions.get(job_id)
        if not job:
            return None
            
        step = StepDefinition(
            step_id=f"step_{uuid.uuid4().hex[:8]}",
            name=name,
            job_id=job_id,
            step_type=step_type,
            chunk_size=chunk_size,
            reader_name=reader_name,
            processor_name=processor_name,
            writer_name=writer_name,
            tasklet_name=tasklet_name,
            skip_limit=skip_limit,
            retry_limit=retry_limit,
            next_step=next_step,
            order=order
        )
        
        self.step_definitions[step.step_id] = step
        job.step_names.append(name)
        
        return step
        
    async def register_reader(self, name: str,
                             reader_type: str,
                             config: Dict[str, Any] = None) -> ItemReader:
        """Регистрация читателя"""
        reader = ItemReader(
            reader_id=f"reader_{uuid.uuid4().hex[:8]}",
            name=name,
            reader_type=reader_type,
            config=config or {}
        )
        
        self.readers[reader.reader_id] = reader
        return reader
        
    async def register_processor(self, name: str,
                                processor_type: str,
                                config: Dict[str, Any] = None) -> ItemProcessor:
        """Регистрация процессора"""
        processor = ItemProcessor(
            processor_id=f"proc_{uuid.uuid4().hex[:8]}",
            name=name,
            processor_type=processor_type,
            config=config or {}
        )
        
        self.processors[processor.processor_id] = processor
        return processor
        
    async def register_writer(self, name: str,
                             writer_type: str,
                             config: Dict[str, Any] = None) -> ItemWriter:
        """Регистрация писателя"""
        writer = ItemWriter(
            writer_id=f"writer_{uuid.uuid4().hex[:8]}",
            name=name,
            writer_type=writer_type,
            config=config or {}
        )
        
        self.writers[writer.writer_id] = writer
        return writer
        
    async def launch_job(self, job_id: str,
                        parameters: Dict[str, Any] = None) -> Optional[JobExecution]:
        """Запуск задания"""
        job = self.job_definitions.get(job_id)
        if not job or not job.is_active:
            return None
            
        # Create job instance
        instance = JobInstance(
            instance_id=f"inst_{uuid.uuid4().hex[:12]}",
            job_id=job_id,
            job_key=json.dumps(parameters or {})
        )
        
        self.job_instances[instance.instance_id] = instance
        
        # Create job execution
        execution = JobExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:12]}",
            job_id=job_id,
            job_instance_id=instance.instance_id,
            status=BatchStatus.STARTING,
            job_parameters=parameters or {}
        )
        
        self.job_executions[execution.execution_id] = execution
        instance.execution_count += 1
        
        # Execute job
        await self._execute_job(execution, job)
        
        return execution
        
    async def _execute_job(self, execution: JobExecution, job: JobDefinition):
        """Выполнение задания"""
        execution.status = BatchStatus.STARTED
        execution.start_time = datetime.now()
        
        # Get steps
        steps = [s for s in self.step_definitions.values() if s.job_id == job.job_id]
        steps.sort(key=lambda s: s.order)
        
        all_success = True
        
        for step in steps:
            step_execution = await self._execute_step(execution, step)
            
            if step_execution.status == StepStatus.FAILED:
                all_success = False
                execution.failure_exceptions.append(f"Step {step.name} failed")
                break
                
        # Update execution status
        if all_success:
            execution.status = BatchStatus.COMPLETED
            execution.exit_status = ExitStatus.COMPLETED
        else:
            execution.status = BatchStatus.FAILED
            execution.exit_status = ExitStatus.FAILED
            
        execution.end_time = datetime.now()
        execution.last_updated = datetime.now()
        
    async def _execute_step(self, job_execution: JobExecution,
                           step: StepDefinition) -> StepExecution:
        """Выполнение шага"""
        step_execution = StepExecution(
            execution_id=f"stepexec_{uuid.uuid4().hex[:8]}",
            step_id=step.step_id,
            job_execution_id=job_execution.execution_id,
            status=StepStatus.STARTING
        )
        
        self.step_executions[step_execution.execution_id] = step_execution
        
        step_execution.status = StepStatus.STARTED
        step_execution.start_time = datetime.now()
        
        if step.step_type == StepType.CHUNK:
            await self._execute_chunk_step(step_execution, step)
        elif step.step_type == StepType.TASKLET:
            await self._execute_tasklet_step(step_execution, step)
        elif step.step_type == StepType.PARTITION:
            await self._execute_partition_step(step_execution, step, job_execution)
            
        step_execution.end_time = datetime.now()
        step_execution.last_updated = datetime.now()
        
        return step_execution
        
    async def _execute_chunk_step(self, step_execution: StepExecution,
                                  step: StepDefinition):
        """Выполнение chunk шага"""
        # Simulate processing
        total_items = random.randint(100, 1000)
        processed = 0
        skipped = 0
        
        chunk_number = 0
        
        while processed < total_items:
            chunk_number += 1
            
            chunk = ChunkContext(
                context_id=f"chunk_{uuid.uuid4().hex[:8]}",
                step_execution_id=step_execution.execution_id,
                chunk_number=chunk_number,
                items_in_chunk=min(step.chunk_size, total_items - processed)
            )
            
            # Process chunk
            success_rate = random.random()
            
            if success_rate > 0.95:  # 5% skip rate
                chunk.items_skipped = random.randint(1, 5)
                skipped += chunk.items_skipped
                
            chunk.items_processed = chunk.items_in_chunk - chunk.items_skipped
            processed += chunk.items_in_chunk
            
            chunk.is_complete = True
            chunk.completed_at = datetime.now()
            
            self.chunk_contexts[chunk.context_id] = chunk
            
            step_execution.commit_count += 1
            
        step_execution.read_count = total_items
        step_execution.write_count = total_items - skipped
        step_execution.skip_count = skipped
        step_execution.filter_count = random.randint(0, 10)
        
        # Determine success
        if random.random() > 0.1:  # 90% success
            step_execution.status = StepStatus.COMPLETED
            step_execution.exit_status = ExitStatus.COMPLETED
        else:
            step_execution.status = StepStatus.FAILED
            step_execution.exit_status = ExitStatus.FAILED
            step_execution.failure_exceptions.append("Processing error")
            
        # Update readers/writers
        for reader in self.readers.values():
            if reader.name == step.reader_name:
                reader.items_read += total_items
                
        for writer in self.writers.values():
            if writer.name == step.writer_name:
                writer.items_written += total_items - skipped
                
    async def _execute_tasklet_step(self, step_execution: StepExecution,
                                   step: StepDefinition):
        """Выполнение tasklet шага"""
        # Simulate tasklet
        if random.random() > 0.1:  # 90% success
            step_execution.status = StepStatus.COMPLETED
            step_execution.exit_status = ExitStatus.COMPLETED
        else:
            step_execution.status = StepStatus.FAILED
            step_execution.exit_status = ExitStatus.FAILED
            step_execution.failure_exceptions.append("Tasklet error")
            
    async def _execute_partition_step(self, step_execution: StepExecution,
                                      step: StepDefinition,
                                      job_execution: JobExecution):
        """Выполнение partition шага"""
        grid_size = 4  # Number of partitions
        
        for i in range(grid_size):
            partition = Partition(
                partition_id=f"part_{uuid.uuid4().hex[:8]}",
                step_id=step.step_id,
                job_execution_id=job_execution.execution_id,
                partition_number=i,
                grid_size=grid_size,
                start_value=i * 1000,
                end_value=(i + 1) * 1000 - 1
            )
            
            # Process partition
            partition.items_processed = random.randint(800, 1000)
            partition.status = StepStatus.COMPLETED
            partition.completed_at = datetime.now()
            
            self.partitions[partition.partition_id] = partition
            
            step_execution.write_count += partition.items_processed
            
        step_execution.read_count = step_execution.write_count
        step_execution.commit_count = grid_size
        step_execution.status = StepStatus.COMPLETED
        step_execution.exit_status = ExitStatus.COMPLETED
        
    async def stop_job(self, execution_id: str) -> bool:
        """Остановка задания"""
        execution = self.job_executions.get(execution_id)
        if not execution or execution.status not in [BatchStatus.STARTING, BatchStatus.STARTED]:
            return False
            
        execution.status = BatchStatus.STOPPING
        execution.status = BatchStatus.STOPPED
        execution.exit_status = ExitStatus.STOPPED
        execution.end_time = datetime.now()
        
        return True
        
    async def restart_job(self, execution_id: str) -> Optional[JobExecution]:
        """Перезапуск задания"""
        old_execution = self.job_executions.get(execution_id)
        if not old_execution:
            return None
            
        job = self.job_definitions.get(old_execution.job_id)
        if not job or not job.restartable:
            return None
            
        # Check restart policy
        if job.restart_policy == RestartPolicy.NEVER:
            return None
        elif job.restart_policy == RestartPolicy.ON_FAILURE:
            if old_execution.status != BatchStatus.FAILED:
                return None
                
        # Launch new execution
        return await self.launch_job(job.job_id, old_execution.job_parameters)
        
    async def abandon_job(self, execution_id: str) -> bool:
        """Прекращение задания"""
        execution = self.job_executions.get(execution_id)
        if not execution:
            return False
            
        execution.status = BatchStatus.ABANDONED
        execution.exit_status = ExitStatus.UNKNOWN
        execution.end_time = datetime.now()
        
        return True
        
    async def add_job_listener(self, name: str,
                              listener_type: str,
                              handler_name: str) -> JobListener:
        """Добавление слушателя задания"""
        listener = JobListener(
            listener_id=f"jl_{uuid.uuid4().hex[:8]}",
            name=name,
            listener_type=listener_type,
            handler_name=handler_name
        )
        
        self.job_listeners[listener.listener_id] = listener
        return listener
        
    async def add_step_listener(self, step_id: str, name: str,
                               listener_type: str,
                               handler_name: str) -> Optional[StepListener]:
        """Добавление слушателя шага"""
        step = self.step_definitions.get(step_id)
        if not step:
            return None
            
        listener = StepListener(
            listener_id=f"sl_{uuid.uuid4().hex[:8]}",
            name=name,
            step_id=step_id,
            listener_type=listener_type,
            handler_name=handler_name
        )
        
        self.step_listeners[listener.listener_id] = listener
        return listener
        
    async def collect_metrics(self, job_id: str) -> Optional[BatchMetrics]:
        """Сбор метрик"""
        job = self.job_definitions.get(job_id)
        if not job:
            return None
            
        executions = [e for e in self.job_executions.values() if e.job_id == job_id]
        
        metrics = BatchMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            job_id=job_id,
            total_executions=len(executions),
            successful_executions=sum(1 for e in executions if e.status == BatchStatus.COMPLETED),
            failed_executions=sum(1 for e in executions if e.status == BatchStatus.FAILED)
        )
        
        # Calculate durations
        completed = [e for e in executions if e.end_time and e.start_time]
        if completed:
            durations = [(e.end_time - e.start_time).total_seconds() for e in completed]
            metrics.avg_duration_seconds = sum(durations) / len(durations)
            metrics.min_duration_seconds = min(durations)
            metrics.max_duration_seconds = max(durations)
            
        # Calculate items
        step_execs = [se for se in self.step_executions.values() 
                     if se.job_execution_id in [e.execution_id for e in executions]]
        
        metrics.total_items_processed = sum(se.write_count for se in step_execs)
        metrics.total_items_skipped = sum(se.skip_count for se in step_execs)
        
        if metrics.avg_duration_seconds > 0:
            metrics.avg_items_per_second = metrics.total_items_processed / (metrics.avg_duration_seconds * len(completed))
            
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_jobs = len(self.job_definitions)
        active_jobs = sum(1 for j in self.job_definitions.values() if j.is_active)
        
        total_executions = len(self.job_executions)
        running_executions = sum(1 for e in self.job_executions.values() if e.status == BatchStatus.STARTED)
        completed_executions = sum(1 for e in self.job_executions.values() if e.status == BatchStatus.COMPLETED)
        failed_executions = sum(1 for e in self.job_executions.values() if e.status == BatchStatus.FAILED)
        
        total_steps = len(self.step_definitions)
        total_step_executions = len(self.step_executions)
        
        total_items_processed = sum(se.write_count for se in self.step_executions.values())
        total_items_skipped = sum(se.skip_count for se in self.step_executions.values())
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_executions": total_executions,
            "running_executions": running_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "total_steps": total_steps,
            "total_step_executions": total_step_executions,
            "total_items_processed": total_items_processed,
            "total_items_skipped": total_items_skipped
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 350: Batch Processing Platform")
    print("=" * 60)
    
    platform = BatchProcessingPlatform()
    print("✓ Batch Processing Platform initialized")
    
    # Register Readers
    print("\n📖 Registering Item Readers...")
    
    readers_data = [
        ("jdbcReader", "jdbc", {"datasource": "primary", "sql": "SELECT * FROM orders", "page_size": 100}),
        ("fileReader", "flat_file", {"resource": "/data/input.csv", "delimiter": ",", "header": True}),
        ("kafkaReader", "kafka", {"topics": ["orders"], "group": "batch", "auto_offset": "earliest"}),
        ("mongoReader", "mongo", {"collection": "users", "query": "{}", "batch_size": 500}),
        ("xmlReader", "xml", {"resource": "/data/input.xml", "root_element": "items"})
    ]
    
    readers = []
    for name, rtype, config in readers_data:
        r = await platform.register_reader(name, rtype, config)
        readers.append(r)
        print(f"  📖 {name} ({rtype})")
        
    # Register Processors
    print("\n⚙️ Registering Item Processors...")
    
    processors_data = [
        ("orderProcessor", "transform", {"mapping": {"total": "amount", "date": "created_at"}}),
        ("validationProcessor", "validation", {"rules": ["required:id", "numeric:amount"]}),
        ("enrichmentProcessor", "enrichment", {"lookup": "customer_details"}),
        ("filterProcessor", "filter", {"criteria": "status != 'cancelled'"}),
        ("aggregationProcessor", "aggregation", {"group_by": "customer_id", "sum": "amount"})
    ]
    
    processors = []
    for name, ptype, config in processors_data:
        p = await platform.register_processor(name, ptype, config)
        processors.append(p)
        print(f"  ⚙️ {name} ({ptype})")
        
    # Register Writers
    print("\n✍️ Registering Item Writers...")
    
    writers_data = [
        ("jdbcWriter", "jdbc", {"datasource": "warehouse", "table": "processed_orders", "batch_size": 100}),
        ("fileWriter", "flat_file", {"resource": "/data/output.csv", "delimiter": ",", "header": True}),
        ("kafkaWriter", "kafka", {"topic": "processed_orders", "key_field": "id"}),
        ("elasticWriter", "elasticsearch", {"index": "orders", "type": "_doc"}),
        ("s3Writer", "s3", {"bucket": "data-lake", "key_prefix": "processed/"})
    ]
    
    writers = []
    for name, wtype, config in writers_data:
        w = await platform.register_writer(name, wtype, config)
        writers.append(w)
        print(f"  ✍️ {name} ({wtype})")
        
    # Create Jobs
    print("\n📦 Creating Batch Jobs...")
    
    jobs_data = [
        ("orderProcessingJob", "Process daily orders from DB to warehouse", True, RestartPolicy.ON_FAILURE, {"date": "2024-01-01"}),
        ("customerImportJob", "Import customers from CSV file", True, RestartPolicy.ALWAYS, {"file": "customers.csv"}),
        ("dataExportJob", "Export processed data to S3", True, RestartPolicy.ON_FAILURE, {"format": "parquet"}),
        ("reportGenerationJob", "Generate daily reports", False, RestartPolicy.NEVER, {"report_type": "daily"}),
        ("dataCleanupJob", "Cleanup old records", True, RestartPolicy.ON_FAILURE, {"retention_days": 90}),
        ("etlPipelineJob", "ETL from Kafka to Elasticsearch", True, RestartPolicy.ALWAYS, {"source": "kafka", "sink": "elastic"})
    ]
    
    jobs = []
    for name, desc, restart, policy, params in jobs_data:
        j = await platform.create_job(name, desc, restart, policy, params)
        jobs.append(j)
        print(f"  📦 {name}")
        
    # Add Steps to Jobs
    print("\n📋 Adding Steps to Jobs...")
    
    # Order Processing Job Steps
    await platform.add_step(jobs[0].job_id, "readOrders", StepType.CHUNK, 100, 
                           "jdbcReader", "validationProcessor", "jdbcWriter", order=1)
    await platform.add_step(jobs[0].job_id, "processOrders", StepType.CHUNK, 50,
                           "jdbcReader", "orderProcessor", "jdbcWriter", order=2)
    await platform.add_step(jobs[0].job_id, "updateStats", StepType.TASKLET, tasklet_name="statsTasklet", order=3)
    print(f"  📋 Added 3 steps to orderProcessingJob")
    
    # Customer Import Job Steps
    await platform.add_step(jobs[1].job_id, "readCustomers", StepType.CHUNK, 200,
                           "fileReader", "validationProcessor", "jdbcWriter", order=1)
    await platform.add_step(jobs[1].job_id, "enrichCustomers", StepType.CHUNK, 100,
                           "jdbcReader", "enrichmentProcessor", "jdbcWriter", order=2)
    print(f"  📋 Added 2 steps to customerImportJob")
    
    # Data Export Job Steps
    await platform.add_step(jobs[2].job_id, "exportData", StepType.PARTITION, order=1)
    print(f"  📋 Added 1 step to dataExportJob")
    
    # ETL Pipeline Job Steps
    await platform.add_step(jobs[5].job_id, "consumeKafka", StepType.CHUNK, 500,
                           "kafkaReader", "orderProcessor", "elasticWriter", order=1)
    await platform.add_step(jobs[5].job_id, "aggregateMetrics", StepType.CHUNK, 100,
                           "elasticWriter", "aggregationProcessor", "jdbcWriter", order=2)
    print(f"  📋 Added 2 steps to etlPipelineJob")
    
    # Launch Jobs
    print("\n▶️ Launching Batch Jobs...")
    
    executions = []
    
    for job in jobs[:4]:
        exec_params = {"run_date": datetime.now().strftime("%Y-%m-%d"), "batch_id": str(uuid.uuid4())[:8]}
        execution = await platform.launch_job(job.job_id, exec_params)
        if execution:
            executions.append(execution)
            print(f"  ▶️ Launched {job.name} ({execution.status.value})")
            
    # Launch additional executions for metrics
    for _ in range(3):
        for job in jobs[:2]:
            execution = await platform.launch_job(job.job_id, {"iteration": random.randint(1, 100)})
            if execution:
                executions.append(execution)
                
    # Add Listeners
    print("\n👂 Adding Listeners...")
    
    await platform.add_job_listener("jobStartListener", "before_job", "onJobStart")
    await platform.add_job_listener("jobEndListener", "after_job", "onJobEnd")
    await platform.add_job_listener("jobFailureListener", "on_failure", "onJobFailure")
    print(f"  👂 Added 3 job listeners")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for job in jobs[:3]:
        m = await platform.collect_metrics(job.job_id)
        if m:
            metrics.append(m)
            
    print(f"  📊 Collected metrics for {len(metrics)} jobs")
    
    # Jobs Dashboard
    print("\n📦 Batch Jobs:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                        │ Description                                   │ Steps │ Restartable │ Restart Policy │ Parameters                                                                                                                                                                                                                                      │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for job in jobs:
        name = job.name[:27].ljust(27)
        desc = job.description[:45].ljust(45)
        steps = str(len(job.step_names)).ljust(5)
        restart = "Yes" if job.restartable else "No"
        restart = restart.ljust(11)
        policy = job.restart_policy.value[:14].ljust(14)
        params = ", ".join([f"{k}={v.value}" for k, v in list(job.parameters.items())[:2]])[:167]
        params = params.ljust(167)
        
        print(f"  │ {name} │ {desc} │ {steps} │ {restart} │ {policy} │ {params} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Steps Dashboard
    print("\n📋 Step Definitions:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job                         │ Step Name             │ Type      │ Chunk Size │ Reader                │ Processor               │ Writer                │ Skip Limit │ Retry Limit                                                                                                                                                                                                         │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for step in platform.step_definitions.values():
        job = platform.job_definitions.get(step.job_id)
        job_name = job.name if job else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        step_name = step.name[:21].ljust(21)
        stype = step.step_type.value[:9].ljust(9)
        chunk = str(step.chunk_size).ljust(10)
        reader = step.reader_name[:21] if step.reader_name else "N/A"
        reader = reader.ljust(21)
        processor = step.processor_name[:23] if step.processor_name else "N/A"
        processor = processor.ljust(23)
        writer = step.writer_name[:21] if step.writer_name else "N/A"
        writer = writer.ljust(21)
        skip = str(step.skip_limit).ljust(10)
        retry = str(step.retry_limit).ljust(149)
        
        print(f"  │ {job_name} │ {step_name} │ {stype} │ {chunk} │ {reader} │ {processor} │ {writer} │ {skip} │ {retry} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Job Executions Dashboard
    print("\n▶️ Job Executions:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Execution ID                │ Job Name                    │ Status       │ Exit Status │ Start Time           │ End Time             │ Duration                                                                                                                                                                                                                                                                                                │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for exec_item in list(executions)[:10]:
        exec_id = exec_item.execution_id[:27].ljust(27)
        
        job = platform.job_definitions.get(exec_item.job_id)
        job_name = job.name if job else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        status_icons = {"starting": "🔄", "started": "🔄", "completed": "✅", "failed": "❌", "stopped": "⏹️", "abandoned": "🚫"}
        status_icon = status_icons.get(exec_item.status.value, "?")
        status = f"{status_icon} {exec_item.status.value}"[:12].ljust(12)
        
        exit_st = exec_item.exit_status.value[:11].ljust(11)
        
        start = exec_item.start_time.strftime("%Y-%m-%d %H:%M:%S") if exec_item.start_time else "N/A"
        start = start[:20].ljust(20)
        
        end = exec_item.end_time.strftime("%Y-%m-%d %H:%M:%S") if exec_item.end_time else "N/A"
        end = end[:20].ljust(20)
        
        if exec_item.start_time and exec_item.end_time:
            dur = (exec_item.end_time - exec_item.start_time).total_seconds()
            duration = f"{dur:.1f}s"
        else:
            duration = "N/A"
        duration = duration[:192].ljust(192)
        
        print(f"  │ {exec_id} │ {job_name} │ {status} │ {exit_st} │ {start} │ {end} │ {duration} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Step Executions
    print("\n📋 Step Executions:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Step Name             │ Status       │ Exit Status │ Read     │ Write    │ Skip   │ Commit │ Duration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for se in list(platform.step_executions.values())[:10]:
        step = platform.step_definitions.get(se.step_id)
        step_name = step.name if step else "Unknown"
        step_name = step_name[:21].ljust(21)
        
        status_icons = {"starting": "🔄", "started": "🔄", "completed": "✅", "failed": "❌", "stopped": "⏹️"}
        status_icon = status_icons.get(se.status.value, "?")
        status = f"{status_icon} {se.status.value}"[:12].ljust(12)
        
        exit_st = se.exit_status.value[:11].ljust(11)
        read = str(se.read_count).ljust(8)
        write = str(se.write_count).ljust(8)
        skip = str(se.skip_count).ljust(6)
        commit = str(se.commit_count).ljust(6)
        
        if se.start_time and se.end_time:
            dur = (se.end_time - se.start_time).total_seconds()
            duration = f"{dur:.1f}s"
        else:
            duration = "N/A"
        duration = duration[:304].ljust(304)
        
        print(f"  │ {step_name} │ {status} │ {exit_st} │ {read} │ {write} │ {skip} │ {commit} │ {duration} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Batch Metrics
    print("\n📊 Batch Job Metrics:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job Name                    │ Total Exec │ Success │ Failed │ Avg Duration │ Items Processed │ Items Skipped │ Throughput/s                                                                                                                                                                                                                                                                                                                                                                                  │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for m in metrics:
        job = platform.job_definitions.get(m.job_id)
        job_name = job.name if job else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        total = str(m.total_executions).ljust(10)
        success = str(m.successful_executions).ljust(7)
        failed = str(m.failed_executions).ljust(6)
        avg_dur = f"{m.avg_duration_seconds:.1f}s".ljust(12)
        processed = str(m.total_items_processed).ljust(15)
        skipped = str(m.total_items_skipped).ljust(13)
        throughput = f"{m.avg_items_per_second:.1f}".ljust(218)
        
        print(f"  │ {job_name} │ {total} │ {success} │ {failed} │ {avg_dur} │ {processed} │ {skipped} │ {throughput} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Jobs: {stats['active_jobs']}/{stats['total_jobs']} active")
    print(f"  Executions: {stats['running_executions']} running, {stats['completed_executions']} completed, {stats['failed_executions']} failed")
    print(f"  Steps: {stats['total_steps']} definitions, {stats['total_step_executions']} executions")
    print(f"  Items: {stats['total_items_processed']} processed, {stats['total_items_skipped']} skipped")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Batch Processing Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Jobs:                  {stats['active_jobs']:>12}                      │")
    print(f"│ Total Executions:             {stats['total_executions']:>12}                      │")
    print(f"│ Total Steps:                  {stats['total_steps']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Running Executions:           {stats['running_executions']:>12}                      │")
    print(f"│ Completed Executions:         {stats['completed_executions']:>12}                      │")
    print(f"│ Failed Executions:            {stats['failed_executions']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Items Processed:              {stats['total_items_processed']:>12}                      │")
    print(f"│ Items Skipped:                {stats['total_items_skipped']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Batch Processing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
