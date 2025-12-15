#!/usr/bin/env python3
"""
Server Init - Iteration 345: Stream Processing Platform
Платформа потоковой обработки данных

Функционал:
- Stream Sources - источники потоков
- Stream Operators - операторы потоков
- Windowing - оконная обработка
- State Management - управление состоянием
- Checkpointing - контрольные точки
- Watermarks - водяные знаки
- Late Data Handling - обработка поздних данных
- Stream Analytics - аналитика потоков
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from enum import Enum
import uuid
import json
import hashlib


class StreamState(Enum):
    """Состояние потока"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


class OperatorType(Enum):
    """Тип оператора"""
    MAP = "map"
    FILTER = "filter"
    FLATMAP = "flatmap"
    KEYBY = "keyby"
    REDUCE = "reduce"
    AGGREGATE = "aggregate"
    JOIN = "join"
    UNION = "union"
    SPLIT = "split"
    SINK = "sink"


class WindowType(Enum):
    """Тип окна"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"


class WatermarkStrategy(Enum):
    """Стратегия водяных знаков"""
    MONOTONIC = "monotonic"
    BOUNDED = "bounded_out_of_orderness"
    PUNCTUATED = "punctuated"
    NO_WATERMARK = "no_watermark"


class CheckpointMode(Enum):
    """Режим контрольных точек"""
    EXACTLY_ONCE = "exactly_once"
    AT_LEAST_ONCE = "at_least_once"


class SourceType(Enum):
    """Тип источника"""
    KAFKA = "kafka"
    KINESIS = "kinesis"
    PUBSUB = "pubsub"
    FILE = "file"
    SOCKET = "socket"
    CUSTOM = "custom"


class SinkType(Enum):
    """Тип приёмника"""
    KAFKA = "kafka"
    DATABASE = "database"
    FILE = "file"
    STDOUT = "stdout"
    HTTP = "http"
    CUSTOM = "custom"


class LateDataPolicy(Enum):
    """Политика поздних данных"""
    DROP = "drop"
    ALLOW = "allow"
    SIDE_OUTPUT = "side_output"


@dataclass
class StreamSource:
    """Источник потока"""
    source_id: str
    name: str
    
    # Type
    source_type: SourceType = SourceType.KAFKA
    
    # Connection
    connection_string: str = ""
    topic: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Parallelism
    parallelism: int = 1
    
    # Watermark
    watermark_strategy: WatermarkStrategy = WatermarkStrategy.BOUNDED
    max_out_of_orderness_ms: int = 5000
    
    # Status
    is_active: bool = True
    
    # Stats
    records_read: int = 0
    bytes_read: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamOperator:
    """Оператор потока"""
    operator_id: str
    name: str
    
    # Type
    operator_type: OperatorType = OperatorType.MAP
    
    # Function
    function_name: str = ""
    function_code: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Parallelism
    parallelism: int = 1
    
    # State
    has_state: bool = False
    state_backend: str = ""
    
    # Input/Output
    input_operators: List[str] = field(default_factory=list)
    output_operators: List[str] = field(default_factory=list)
    
    # Stats
    records_in: int = 0
    records_out: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamWindow:
    """Окно потока"""
    window_id: str
    name: str
    
    # Type
    window_type: WindowType = WindowType.TUMBLING
    
    # Size
    size_ms: int = 60000  # 1 minute
    slide_ms: int = 0  # For sliding windows
    gap_ms: int = 0  # For session windows
    
    # Trigger
    trigger_type: str = "event_time"  # event_time, processing_time, count
    trigger_threshold: int = 0
    
    # Late data
    late_data_policy: LateDataPolicy = LateDataPolicy.DROP
    allowed_lateness_ms: int = 0
    
    # State
    is_active: bool = True
    
    # Stats
    windows_created: int = 0
    windows_fired: int = 0
    late_records: int = 0


@dataclass
class StreamSink:
    """Приёмник потока"""
    sink_id: str
    name: str
    
    # Type
    sink_type: SinkType = SinkType.KAFKA
    
    # Connection
    connection_string: str = ""
    target: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Parallelism
    parallelism: int = 1
    
    # Status
    is_active: bool = True
    
    # Stats
    records_written: int = 0
    bytes_written: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamJob:
    """Задание потоковой обработки"""
    job_id: str
    name: str
    
    # Status
    state: StreamState = StreamState.CREATED
    
    # Components
    source_ids: List[str] = field(default_factory=list)
    operator_ids: List[str] = field(default_factory=list)
    sink_ids: List[str] = field(default_factory=list)
    
    # Checkpointing
    checkpoint_mode: CheckpointMode = CheckpointMode.EXACTLY_ONCE
    checkpoint_interval_ms: int = 60000
    
    # Parallelism
    default_parallelism: int = 1
    
    # Resources
    task_managers: int = 1
    slots_per_manager: int = 4
    
    # Stats
    records_processed: int = 0
    errors: int = 0
    uptime_seconds: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None


@dataclass
class Checkpoint:
    """Контрольная точка"""
    checkpoint_id: str
    job_id: str
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    
    # Size
    state_size_bytes: int = 0
    
    # Duration
    duration_ms: int = 0
    
    # Alignment
    alignment_duration_ms: int = 0
    
    # Timestamps
    trigger_timestamp: datetime = field(default_factory=datetime.now)
    completion_timestamp: Optional[datetime] = None


@dataclass
class Watermark:
    """Водяной знак"""
    watermark_id: str
    source_id: str
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Progress
    event_time: datetime = field(default_factory=datetime.now)
    
    # Lag
    lag_ms: int = 0


@dataclass
class StateSnapshot:
    """Снимок состояния"""
    snapshot_id: str
    operator_id: str
    
    # State
    state_data: Dict[str, Any] = field(default_factory=dict)
    state_size_bytes: int = 0
    
    # Checkpoint
    checkpoint_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamRecord:
    """Запись потока"""
    record_id: str
    
    # Key/Value
    key: str = ""
    value: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    event_time: datetime = field(default_factory=datetime.now)
    processing_time: datetime = field(default_factory=datetime.now)
    ingestion_time: datetime = field(default_factory=datetime.now)
    
    # Metadata
    partition: int = 0
    offset: int = 0


@dataclass
class WindowResult:
    """Результат окна"""
    result_id: str
    window_id: str
    
    # Window bounds
    window_start: datetime = field(default_factory=datetime.now)
    window_end: datetime = field(default_factory=datetime.now)
    
    # Key
    key: str = ""
    
    # Result
    result: Any = None
    record_count: int = 0
    
    # Timestamps
    fired_at: datetime = field(default_factory=datetime.now)


@dataclass
class StreamMetrics:
    """Метрики потока"""
    metrics_id: str
    job_id: str
    
    # Throughput
    records_per_second: float = 0.0
    bytes_per_second: float = 0.0
    
    # Latency
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Backpressure
    backpressure_ratio: float = 0.0
    
    # State
    state_size_bytes: int = 0
    
    # Checkpoints
    checkpoint_duration_ms: float = 0.0
    
    # Timestamp
    collected_at: datetime = field(default_factory=datetime.now)


class StreamPlatform:
    """Платформа потоковой обработки"""
    
    def __init__(self):
        self.sources: Dict[str, StreamSource] = {}
        self.operators: Dict[str, StreamOperator] = {}
        self.windows: Dict[str, StreamWindow] = {}
        self.sinks: Dict[str, StreamSink] = {}
        self.jobs: Dict[str, StreamJob] = {}
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.watermarks: Dict[str, Watermark] = {}
        self.state_snapshots: Dict[str, StateSnapshot] = {}
        self.metrics: Dict[str, StreamMetrics] = {}
        self.window_results: Dict[str, WindowResult] = {}
        
    async def create_source(self, name: str,
                           source_type: SourceType,
                           connection_string: str = "",
                           topic: str = "",
                           parallelism: int = 1,
                           watermark_strategy: WatermarkStrategy = WatermarkStrategy.BOUNDED,
                           max_out_of_orderness_ms: int = 5000,
                           config: Dict[str, Any] = None) -> StreamSource:
        """Создание источника"""
        source = StreamSource(
            source_id=f"src_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            connection_string=connection_string,
            topic=topic,
            parallelism=parallelism,
            watermark_strategy=watermark_strategy,
            max_out_of_orderness_ms=max_out_of_orderness_ms,
            config=config or {}
        )
        
        self.sources[source.source_id] = source
        return source
        
    async def create_operator(self, name: str,
                             operator_type: OperatorType,
                             function_name: str = "",
                             function_code: str = "",
                             parallelism: int = 1,
                             has_state: bool = False,
                             state_backend: str = "",
                             config: Dict[str, Any] = None) -> StreamOperator:
        """Создание оператора"""
        operator = StreamOperator(
            operator_id=f"op_{uuid.uuid4().hex[:8]}",
            name=name,
            operator_type=operator_type,
            function_name=function_name,
            function_code=function_code,
            parallelism=parallelism,
            has_state=has_state,
            state_backend=state_backend,
            config=config or {}
        )
        
        self.operators[operator.operator_id] = operator
        return operator
        
    async def create_window(self, name: str,
                           window_type: WindowType,
                           size_ms: int = 60000,
                           slide_ms: int = 0,
                           gap_ms: int = 0,
                           trigger_type: str = "event_time",
                           late_data_policy: LateDataPolicy = LateDataPolicy.DROP,
                           allowed_lateness_ms: int = 0) -> StreamWindow:
        """Создание окна"""
        window = StreamWindow(
            window_id=f"win_{uuid.uuid4().hex[:8]}",
            name=name,
            window_type=window_type,
            size_ms=size_ms,
            slide_ms=slide_ms,
            gap_ms=gap_ms,
            trigger_type=trigger_type,
            late_data_policy=late_data_policy,
            allowed_lateness_ms=allowed_lateness_ms
        )
        
        self.windows[window.window_id] = window
        return window
        
    async def create_sink(self, name: str,
                         sink_type: SinkType,
                         connection_string: str = "",
                         target: str = "",
                         parallelism: int = 1,
                         config: Dict[str, Any] = None) -> StreamSink:
        """Создание приёмника"""
        sink = StreamSink(
            sink_id=f"sink_{uuid.uuid4().hex[:8]}",
            name=name,
            sink_type=sink_type,
            connection_string=connection_string,
            target=target,
            parallelism=parallelism,
            config=config or {}
        )
        
        self.sinks[sink.sink_id] = sink
        return sink
        
    async def create_job(self, name: str,
                        source_ids: List[str],
                        operator_ids: List[str],
                        sink_ids: List[str],
                        checkpoint_mode: CheckpointMode = CheckpointMode.EXACTLY_ONCE,
                        checkpoint_interval_ms: int = 60000,
                        default_parallelism: int = 1,
                        task_managers: int = 1,
                        slots_per_manager: int = 4) -> StreamJob:
        """Создание задания"""
        job = StreamJob(
            job_id=f"job_{uuid.uuid4().hex[:12]}",
            name=name,
            source_ids=source_ids,
            operator_ids=operator_ids,
            sink_ids=sink_ids,
            checkpoint_mode=checkpoint_mode,
            checkpoint_interval_ms=checkpoint_interval_ms,
            default_parallelism=default_parallelism,
            task_managers=task_managers,
            slots_per_manager=slots_per_manager
        )
        
        self.jobs[job.job_id] = job
        return job
        
    async def start_job(self, job_id: str) -> bool:
        """Запуск задания"""
        job = self.jobs.get(job_id)
        if not job or job.state == StreamState.RUNNING:
            return False
            
        job.state = StreamState.RUNNING
        job.started_at = datetime.now()
        
        # Simulate job execution
        await self._simulate_job_execution(job)
        
        return True
        
    async def _simulate_job_execution(self, job: StreamJob):
        """Симуляция выполнения задания"""
        for _ in range(10):
            # Simulate records processing
            records = random.randint(100, 1000)
            job.records_processed += records
            
            # Update sources
            for src_id in job.source_ids:
                src = self.sources.get(src_id)
                if src:
                    src.records_read += records // len(job.source_ids)
                    src.bytes_read += records * 100
                    
            # Update operators
            for op_id in job.operator_ids:
                op = self.operators.get(op_id)
                if op:
                    op.records_in += records // len(job.operator_ids)
                    op.records_out += int(records * 0.9)  # Some filtering
                    
            # Update sinks
            for sink_id in job.sink_ids:
                sink = self.sinks.get(sink_id)
                if sink:
                    sink.records_written += records // len(job.sink_ids)
                    sink.bytes_written += records * 80
                    
        job.uptime_seconds = random.randint(300, 3600)
        
    async def stop_job(self, job_id: str) -> bool:
        """Остановка задания"""
        job = self.jobs.get(job_id)
        if not job or job.state != StreamState.RUNNING:
            return False
            
        job.state = StreamState.STOPPED
        job.stopped_at = datetime.now()
        return True
        
    async def trigger_checkpoint(self, job_id: str) -> Optional[Checkpoint]:
        """Создание контрольной точки"""
        job = self.jobs.get(job_id)
        if not job or job.state != StreamState.RUNNING:
            return None
            
        checkpoint = Checkpoint(
            checkpoint_id=f"ckpt_{uuid.uuid4().hex[:8]}",
            job_id=job_id,
            status="in_progress"
        )
        
        # Simulate checkpoint
        await asyncio.sleep(0.01)
        
        checkpoint.status = "completed"
        checkpoint.state_size_bytes = random.randint(1000000, 10000000)
        checkpoint.duration_ms = random.randint(100, 2000)
        checkpoint.alignment_duration_ms = random.randint(10, 200)
        checkpoint.completion_timestamp = datetime.now()
        
        # Create state snapshots
        for op_id in job.operator_ids:
            op = self.operators.get(op_id)
            if op and op.has_state:
                snapshot = StateSnapshot(
                    snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
                    operator_id=op_id,
                    state_data={"count": random.randint(1000, 10000)},
                    state_size_bytes=random.randint(10000, 100000),
                    checkpoint_id=checkpoint.checkpoint_id
                )
                self.state_snapshots[snapshot.snapshot_id] = snapshot
                
        self.checkpoints[checkpoint.checkpoint_id] = checkpoint
        return checkpoint
        
    async def emit_watermark(self, source_id: str,
                            event_time: datetime) -> Optional[Watermark]:
        """Генерация водяного знака"""
        source = self.sources.get(source_id)
        if not source:
            return None
            
        watermark = Watermark(
            watermark_id=f"wm_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            event_time=event_time,
            lag_ms=int((datetime.now() - event_time).total_seconds() * 1000)
        )
        
        self.watermarks[watermark.watermark_id] = watermark
        return watermark
        
    async def fire_window(self, window_id: str,
                         key: str,
                         result: Any,
                         record_count: int,
                         window_start: datetime,
                         window_end: datetime) -> WindowResult:
        """Запуск окна"""
        window = self.windows.get(window_id)
        if window:
            window.windows_fired += 1
            
        win_result = WindowResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            window_id=window_id,
            window_start=window_start,
            window_end=window_end,
            key=key,
            result=result,
            record_count=record_count
        )
        
        self.window_results[win_result.result_id] = win_result
        return win_result
        
    async def collect_metrics(self, job_id: str) -> Optional[StreamMetrics]:
        """Сбор метрик"""
        job = self.jobs.get(job_id)
        if not job:
            return None
            
        metrics = StreamMetrics(
            metrics_id=f"met_{uuid.uuid4().hex[:8]}",
            job_id=job_id,
            records_per_second=random.uniform(1000, 50000),
            bytes_per_second=random.uniform(100000, 5000000),
            avg_latency_ms=random.uniform(10, 100),
            p99_latency_ms=random.uniform(50, 500),
            backpressure_ratio=random.uniform(0, 0.3),
            state_size_bytes=random.randint(10000000, 100000000)
        )
        
        # Calculate checkpoint metrics
        job_checkpoints = [c for c in self.checkpoints.values() if c.job_id == job_id]
        if job_checkpoints:
            metrics.checkpoint_duration_ms = sum(c.duration_ms for c in job_checkpoints) / len(job_checkpoints)
            
        self.metrics[metrics.metrics_id] = metrics
        return metrics
        
    async def connect_operators(self, from_op_id: str, to_op_id: str) -> bool:
        """Соединение операторов"""
        from_op = self.operators.get(from_op_id)
        to_op = self.operators.get(to_op_id)
        
        if not from_op or not to_op:
            return False
            
        from_op.output_operators.append(to_op_id)
        to_op.input_operators.append(from_op_id)
        return True
        
    def get_job_topology(self, job_id: str) -> Dict[str, List[str]]:
        """Получение топологии задания"""
        job = self.jobs.get(job_id)
        if not job:
            return {}
            
        topology = {}
        
        # Sources
        for src_id in job.source_ids:
            source = self.sources.get(src_id)
            if source:
                topology[f"source:{source.name}"] = []
                
        # Operators
        for op_id in job.operator_ids:
            op = self.operators.get(op_id)
            if op:
                topology[f"op:{op.name}"] = op.output_operators
                
        # Sinks
        for sink_id in job.sink_ids:
            sink = self.sinks.get(sink_id)
            if sink:
                topology[f"sink:{sink.name}"] = []
                
        return topology
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_sources = len(self.sources)
        active_sources = sum(1 for s in self.sources.values() if s.is_active)
        
        total_operators = len(self.operators)
        stateful_operators = sum(1 for o in self.operators.values() if o.has_state)
        
        total_windows = len(self.windows)
        
        total_sinks = len(self.sinks)
        active_sinks = sum(1 for s in self.sinks.values() if s.is_active)
        
        total_jobs = len(self.jobs)
        running_jobs = sum(1 for j in self.jobs.values() if j.state == StreamState.RUNNING)
        
        total_checkpoints = len(self.checkpoints)
        completed_checkpoints = sum(1 for c in self.checkpoints.values() if c.status == "completed")
        
        total_records = sum(j.records_processed for j in self.jobs.values())
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_operators": total_operators,
            "stateful_operators": stateful_operators,
            "total_windows": total_windows,
            "total_sinks": total_sinks,
            "active_sinks": active_sinks,
            "total_jobs": total_jobs,
            "running_jobs": running_jobs,
            "total_checkpoints": total_checkpoints,
            "completed_checkpoints": completed_checkpoints,
            "total_records": total_records
        }


# Demo
async def main():
    print("=" * 60)
    print("Server Init - Iteration 345: Stream Processing Platform")
    print("=" * 60)
    
    platform = StreamPlatform()
    print("✓ Stream Platform initialized")
    
    # Create Sources
    print("\n📥 Creating Stream Sources...")
    
    sources_data = [
        ("User Events", SourceType.KAFKA, "kafka://broker:9092", "user-events", 4, WatermarkStrategy.BOUNDED, 5000),
        ("Order Events", SourceType.KAFKA, "kafka://broker:9092", "order-events", 8, WatermarkStrategy.BOUNDED, 10000),
        ("Clickstream", SourceType.KINESIS, "kinesis://us-east-1", "clickstream", 16, WatermarkStrategy.BOUNDED, 3000),
        ("IoT Sensors", SourceType.PUBSUB, "pubsub://project-id", "iot-sensors", 4, WatermarkStrategy.MONOTONIC, 1000),
        ("Log Stream", SourceType.KAFKA, "kafka://broker:9092", "application-logs", 4, WatermarkStrategy.NO_WATERMARK, 0)
    ]
    
    sources = []
    for name, stype, conn, topic, par, wm, oo in sources_data:
        src = await platform.create_source(name, stype, conn, topic, par, wm, oo)
        sources.append(src)
        print(f"  📥 {name} ({stype.value}, {par} partitions)")
        
    # Create Operators
    print("\n⚙️ Creating Stream Operators...")
    
    operators_data = [
        ("Parse JSON", OperatorType.MAP, "parse_json", "", 4, False, ""),
        ("Filter Valid", OperatorType.FILTER, "is_valid", "", 4, False, ""),
        ("Extract Fields", OperatorType.MAP, "extract_fields", "", 4, False, ""),
        ("Key By User", OperatorType.KEYBY, "get_user_id", "", 4, False, ""),
        ("Count Events", OperatorType.AGGREGATE, "count", "", 4, True, "rocksdb"),
        ("Sum Values", OperatorType.REDUCE, "sum_values", "", 4, True, "rocksdb"),
        ("Join Orders", OperatorType.JOIN, "join_on_order_id", "", 8, True, "rocksdb"),
        ("Flatten Array", OperatorType.FLATMAP, "flatten_items", "", 4, False, ""),
        ("Route Events", OperatorType.SPLIT, "route_by_type", "", 4, False, ""),
        ("Merge Streams", OperatorType.UNION, "merge", "", 4, False, "")
    ]
    
    operators = []
    for name, otype, func, code, par, state, backend in operators_data:
        op = await platform.create_operator(name, otype, func, code, par, state, backend)
        operators.append(op)
        state_str = " (stateful)" if state else ""
        print(f"  ⚙️ {name} ({otype.value}{state_str})")
        
    # Connect Operators
    print("\n🔗 Connecting Operators...")
    
    await platform.connect_operators(operators[0].operator_id, operators[1].operator_id)
    await platform.connect_operators(operators[1].operator_id, operators[2].operator_id)
    await platform.connect_operators(operators[2].operator_id, operators[3].operator_id)
    await platform.connect_operators(operators[3].operator_id, operators[4].operator_id)
    await platform.connect_operators(operators[4].operator_id, operators[5].operator_id)
    
    print(f"  🔗 Created operator pipeline")
    
    # Create Windows
    print("\n🪟 Creating Windows...")
    
    windows_data = [
        ("1-Minute Tumbling", WindowType.TUMBLING, 60000, 0, 0, "event_time", LateDataPolicy.ALLOW, 5000),
        ("5-Minute Sliding", WindowType.SLIDING, 300000, 60000, 0, "event_time", LateDataPolicy.SIDE_OUTPUT, 10000),
        ("Session Window", WindowType.SESSION, 0, 0, 30000, "event_time", LateDataPolicy.DROP, 0),
        ("1-Hour Tumbling", WindowType.TUMBLING, 3600000, 0, 0, "event_time", LateDataPolicy.ALLOW, 60000),
        ("Count Window", WindowType.GLOBAL, 0, 0, 0, "count", LateDataPolicy.DROP, 0)
    ]
    
    windows = []
    for name, wtype, size, slide, gap, trigger, late, lateness in windows_data:
        win = await platform.create_window(name, wtype, size, slide, gap, trigger, late, lateness)
        windows.append(win)
        print(f"  🪟 {name} ({wtype.value})")
        
    # Create Sinks
    print("\n📤 Creating Stream Sinks...")
    
    sinks_data = [
        ("Processed Events", SinkType.KAFKA, "kafka://broker:9092", "processed-events", 4),
        ("Analytics DB", SinkType.DATABASE, "jdbc:postgresql://db:5432/analytics", "events_table", 2),
        ("Archive Storage", SinkType.FILE, "s3://bucket/archive/", "events/", 1),
        ("Dashboard API", SinkType.HTTP, "https://api.dashboard.io/events", "/ingest", 2),
        ("Debug Output", SinkType.STDOUT, "", "", 1)
    ]
    
    sinks = []
    for name, stype, conn, target, par in sinks_data:
        sink = await platform.create_sink(name, stype, conn, target, par)
        sinks.append(sink)
        print(f"  📤 {name} ({stype.value})")
        
    # Create Jobs
    print("\n🎯 Creating Stream Jobs...")
    
    jobs_data = [
        ("User Analytics Pipeline", [sources[0].source_id], operators[:5], [sinks[0].sink_id, sinks[1].sink_id], CheckpointMode.EXACTLY_ONCE, 60000, 4, 2, 4),
        ("Order Processing", [sources[1].source_id], operators[2:6], [sinks[0].sink_id], CheckpointMode.EXACTLY_ONCE, 30000, 8, 4, 4),
        ("Clickstream Analysis", [sources[2].source_id], operators[:4], [sinks[1].sink_id, sinks[2].sink_id], CheckpointMode.AT_LEAST_ONCE, 120000, 16, 8, 4),
        ("IoT Aggregation", [sources[3].source_id], operators[3:6], [sinks[0].sink_id, sinks[3].sink_id], CheckpointMode.EXACTLY_ONCE, 60000, 4, 2, 4),
        ("Log Processing", [sources[4].source_id], operators[:3], [sinks[2].sink_id], CheckpointMode.AT_LEAST_ONCE, 300000, 4, 1, 4)
    ]
    
    jobs = []
    for name, src_ids, ops, sink_ids, ckpt_mode, ckpt_int, par, tm, slots in jobs_data:
        job = await platform.create_job(
            name, src_ids, 
            [o.operator_id for o in ops],
            sink_ids, ckpt_mode, ckpt_int, par, tm, slots
        )
        jobs.append(job)
        print(f"  🎯 {name} (parallelism: {par})")
        
    # Start Jobs
    print("\n▶️ Starting Jobs...")
    
    for job in jobs[:3]:
        await platform.start_job(job.job_id)
        print(f"  ▶️ {job.name}: {job.state.value}")
        
    # Trigger Checkpoints
    print("\n💾 Triggering Checkpoints...")
    
    checkpoints = []
    for job in jobs[:3]:
        if job.state == StreamState.RUNNING:
            for _ in range(3):
                ckpt = await platform.trigger_checkpoint(job.job_id)
                if ckpt:
                    checkpoints.append(ckpt)
                    
    print(f"  💾 Created {len(checkpoints)} checkpoints")
    
    # Emit Watermarks
    print("\n💧 Emitting Watermarks...")
    
    watermarks = []
    for source in sources:
        for i in range(5):
            event_time = datetime.now() - timedelta(seconds=random.randint(1, 10))
            wm = await platform.emit_watermark(source.source_id, event_time)
            if wm:
                watermarks.append(wm)
                
    print(f"  💧 Emitted {len(watermarks)} watermarks")
    
    # Fire Windows
    print("\n🔔 Firing Windows...")
    
    window_results = []
    for win in windows[:3]:
        for i in range(5):
            now = datetime.now()
            result = await platform.fire_window(
                win.window_id,
                f"user_{random.randint(1, 100)}",
                {"count": random.randint(10, 1000), "sum": random.uniform(100, 10000)},
                random.randint(50, 500),
                now - timedelta(minutes=1),
                now
            )
            window_results.append(result)
            
    print(f"  🔔 Fired {len(window_results)} windows")
    
    # Collect Metrics
    print("\n📊 Collecting Metrics...")
    
    metrics = []
    for job in jobs[:3]:
        met = await platform.collect_metrics(job.job_id)
        if met:
            metrics.append(met)
            print(f"  📊 {job.name}: {met.records_per_second:.0f} rec/s, {met.avg_latency_ms:.1f}ms avg")
            
    # Stream Sources Dashboard
    print("\n📥 Stream Sources:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Type     │ Topic                │ Parallelism │ Watermark Strategy │ Records Read │ Bytes Read │ Status                                       │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for src in sources:
        name = src.name[:19].ljust(19)
        stype = src.source_type.value[:8].ljust(8)
        topic = src.topic[:20].ljust(20)
        par = str(src.parallelism).ljust(11)
        wm = src.watermark_strategy.value[:18].ljust(18)
        records = f"{src.records_read:,}".ljust(12)
        bytes_r = f"{src.bytes_read // 1024:,} KB".ljust(10)
        status = "🟢 Active" if src.is_active else "⚫ Inactive"
        status = status[:46].ljust(46)
        
        print(f"  │ {name} │ {stype} │ {topic} │ {par} │ {wm} │ {records} │ {bytes_r} │ {status} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Stream Operators
    print("\n⚙️ Stream Operators:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                │ Type      │ Function            │ Parallelism │ Stateful │ Records In │ Records Out │ State Backend                               │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for op in operators:
        name = op.name[:19].ljust(19)
        otype = op.operator_type.value[:9].ljust(9)
        func = op.function_name[:19].ljust(19)
        par = str(op.parallelism).ljust(11)
        stateful = "Yes" if op.has_state else "No"
        stateful = stateful.ljust(8)
        rec_in = f"{op.records_in:,}".ljust(10)
        rec_out = f"{op.records_out:,}".ljust(11)
        backend = op.state_backend if op.state_backend else "N/A"
        backend = backend[:45].ljust(45)
        
        print(f"  │ {name} │ {otype} │ {func} │ {par} │ {stateful} │ {rec_in} │ {rec_out} │ {backend} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Windows
    print("\n🪟 Windows:")
    
    print("\n  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                  │ Type      │ Size      │ Slide     │ Trigger      │ Late Policy  │ Created │ Fired │ Late Records                                        │")
    print("  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for win in windows:
        name = win.name[:21].ljust(21)
        wtype = win.window_type.value[:9].ljust(9)
        
        size = f"{win.size_ms // 1000}s" if win.size_ms > 0 else "N/A"
        size = size[:9].ljust(9)
        
        slide = f"{win.slide_ms // 1000}s" if win.slide_ms > 0 else "N/A"
        slide = slide[:9].ljust(9)
        
        trigger = win.trigger_type[:12].ljust(12)
        late = win.late_data_policy.value[:12].ljust(12)
        created = str(win.windows_created).ljust(7)
        fired = str(win.windows_fired).ljust(5)
        late_rec = str(win.late_records).ljust(53)
        
        print(f"  │ {name} │ {wtype} │ {size} │ {slide} │ {trigger} │ {late} │ {created} │ {fired} │ {late_rec} │")
        
    print("  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Stream Jobs
    print("\n🎯 Stream Jobs:")
    
    print("\n  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Name                        │ State    │ Parallelism │ Checkpoint Mode │ Checkpoint Interval │ Records Processed │ Uptime │ Task Managers │ Started                                                                    │")
    print("  ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for job in jobs:
        name = job.name[:27].ljust(27)
        
        state_icons = {"created": "⚪", "running": "🟢", "paused": "🟡", "stopped": "⚫", "failed": "🔴"}
        state_icon = state_icons.get(job.state.value, "?")
        state = f"{state_icon} {job.state.value}"[:8].ljust(8)
        
        par = str(job.default_parallelism).ljust(11)
        ckpt_mode = job.checkpoint_mode.value[:15].ljust(15)
        ckpt_int = f"{job.checkpoint_interval_ms // 1000}s".ljust(19)
        records = f"{job.records_processed:,}".ljust(17)
        uptime = f"{job.uptime_seconds // 60}m".ljust(6)
        tm = str(job.task_managers).ljust(13)
        
        started = job.started_at.strftime("%Y-%m-%d %H:%M:%S") if job.started_at else "Not started"
        started = started[:76].ljust(76)
        
        print(f"  │ {name} │ {state} │ {par} │ {ckpt_mode} │ {ckpt_int} │ {records} │ {uptime} │ {tm} │ {started} │")
        
    print("  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Checkpoints
    print("\n💾 Recent Checkpoints:")
    
    print("\n  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job                         │ Status    │ State Size │ Duration │ Alignment │ Triggered            │ Completed                                                                                                  │")
    print("  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for ckpt in list(checkpoints)[:10]:
        job = platform.jobs.get(ckpt.job_id)
        job_name = job.name if job else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        status_icons = {"pending": "⏳", "in_progress": "🔄", "completed": "✓", "failed": "✗"}
        status_icon = status_icons.get(ckpt.status, "?")
        status = f"{status_icon} {ckpt.status}"[:9].ljust(9)
        
        size = f"{ckpt.state_size_bytes // 1024:,} KB".ljust(10)
        duration = f"{ckpt.duration_ms}ms".ljust(8)
        alignment = f"{ckpt.alignment_duration_ms}ms".ljust(9)
        triggered = ckpt.trigger_timestamp.strftime("%Y-%m-%d %H:%M:%S")[:20].ljust(20)
        
        completed = ckpt.completion_timestamp.strftime("%Y-%m-%d %H:%M:%S") if ckpt.completion_timestamp else "N/A"
        completed = completed[:108].ljust(108)
        
        print(f"  │ {job_name} │ {status} │ {size} │ {duration} │ {alignment} │ {triggered} │ {completed} │")
        
    print("  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Metrics
    print("\n📊 Job Metrics:")
    
    print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("  │ Job                         │ Records/s │ Bytes/s    │ Avg Latency │ P99 Latency │ Backpressure │ State Size │ Checkpoint Duration                                                                                       │")
    print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
    
    for met in metrics:
        job = platform.jobs.get(met.job_id)
        job_name = job.name if job else "Unknown"
        job_name = job_name[:27].ljust(27)
        
        rps = f"{met.records_per_second:,.0f}".ljust(9)
        bps = f"{met.bytes_per_second / 1024 / 1024:.1f} MB/s".ljust(10)
        avg_lat = f"{met.avg_latency_ms:.1f}ms".ljust(11)
        p99_lat = f"{met.p99_latency_ms:.1f}ms".ljust(11)
        bp = f"{met.backpressure_ratio * 100:.1f}%".ljust(12)
        state = f"{met.state_size_bytes // 1024 // 1024} MB".ljust(10)
        ckpt_dur = f"{met.checkpoint_duration_ms:.0f}ms".ljust(103)
        
        print(f"  │ {job_name} │ {rps} │ {bps} │ {avg_lat} │ {p99_lat} │ {bp} │ {state} │ {ckpt_dur} │")
        
    print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
    
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📊 Overall Statistics:")
    
    print(f"\n  Sources: {stats['active_sources']}/{stats['total_sources']} active")
    print(f"  Operators: {stats['total_operators']} ({stats['stateful_operators']} stateful)")
    print(f"  Windows: {stats['total_windows']}")
    print(f"  Sinks: {stats['active_sinks']}/{stats['total_sinks']} active")
    print(f"  Jobs: {stats['running_jobs']}/{stats['total_jobs']} running")
    print(f"  Checkpoints: {stats['completed_checkpoints']}/{stats['total_checkpoints']} completed")
    print(f"  Total Records: {stats['total_records']:,}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Stream Processing Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Sources:               {stats['active_sources']:>12}                      │")
    print(f"│ Stream Operators:             {stats['total_operators']:>12}                      │")
    print(f"│ Running Jobs:                 {stats['running_jobs']:>12}                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Records:                {stats['total_records']:>12,}                      │")
    print(f"│ Checkpoints:                  {stats['completed_checkpoints']:>12}                      │")
    print(f"│ Stateful Operators:           {stats['stateful_operators']:>12}                      │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Stream Processing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
