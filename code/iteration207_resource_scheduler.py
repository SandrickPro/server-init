#!/usr/bin/env python3
"""
Server Init - Iteration 207: Resource Scheduler Platform
Платформа планирования ресурсов

Функционал:
- Resource Allocation - распределение ресурсов
- Job Scheduling - планирование задач
- Capacity Planning - планирование ёмкости
- Queue Management - управление очередями
- Priority Scheduling - приоритетное планирование
- Affinity Rules - правила размещения
- Resource Limits - лимиты ресурсов
- Scheduling Metrics - метрики планирования
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import heapq


class ResourceType(Enum):
    """Тип ресурса"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


class JobStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PREEMPTED = "preempted"


class JobPriority(Enum):
    """Приоритет задачи"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class SchedulingPolicy(Enum):
    """Политика планирования"""
    FIFO = "fifo"
    PRIORITY = "priority"
    FAIR_SHARE = "fair_share"
    ROUND_ROBIN = "round_robin"


@dataclass
class ResourceCapacity:
    """Ёмкость ресурса"""
    cpu_cores: float = 0
    memory_mb: int = 0
    gpu_units: int = 0
    storage_gb: int = 0
    
    def __sub__(self, other: 'ResourceCapacity') -> 'ResourceCapacity':
        return ResourceCapacity(
            cpu_cores=self.cpu_cores - other.cpu_cores,
            memory_mb=self.memory_mb - other.memory_mb,
            gpu_units=self.gpu_units - other.gpu_units,
            storage_gb=self.storage_gb - other.storage_gb
        )
        
    def can_fit(self, request: 'ResourceRequest') -> bool:
        return (self.cpu_cores >= request.cpu_cores and
                self.memory_mb >= request.memory_mb and
                self.gpu_units >= request.gpu_units and
                self.storage_gb >= request.storage_gb)


@dataclass
class ResourceRequest:
    """Запрос ресурсов"""
    cpu_cores: float = 0.5
    memory_mb: int = 512
    gpu_units: int = 0
    storage_gb: int = 1


@dataclass
class Node:
    """Узел кластера"""
    node_id: str
    name: str = ""
    
    # Capacity
    total_capacity: ResourceCapacity = field(default_factory=ResourceCapacity)
    allocated_capacity: ResourceCapacity = field(default_factory=ResourceCapacity)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Status
    healthy: bool = True
    schedulable: bool = True
    
    # Jobs
    running_jobs: List[str] = field(default_factory=list)
    
    @property
    def available_capacity(self) -> ResourceCapacity:
        return ResourceCapacity(
            cpu_cores=self.total_capacity.cpu_cores - self.allocated_capacity.cpu_cores,
            memory_mb=self.total_capacity.memory_mb - self.allocated_capacity.memory_mb,
            gpu_units=self.total_capacity.gpu_units - self.allocated_capacity.gpu_units,
            storage_gb=self.total_capacity.storage_gb - self.allocated_capacity.storage_gb
        )


@dataclass
class Job:
    """Задача"""
    job_id: str
    name: str = ""
    
    # Resources
    resource_request: ResourceRequest = field(default_factory=ResourceRequest)
    
    # Priority
    priority: JobPriority = JobPriority.MEDIUM
    
    # Scheduling
    status: JobStatus = JobStatus.PENDING
    assigned_node: Optional[str] = None
    
    # Constraints
    node_selector: Dict[str, str] = field(default_factory=dict)
    tolerations: List[str] = field(default_factory=list)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Duration
    estimated_duration_seconds: int = 60
    
    def __lt__(self, other: 'Job'):
        # For priority queue - higher priority first
        return self.priority.value > other.priority.value


@dataclass
class Queue:
    """Очередь задач"""
    queue_id: str
    name: str = ""
    
    # Policy
    policy: SchedulingPolicy = SchedulingPolicy.FIFO
    
    # Limits
    max_jobs: int = 100
    weight: int = 1
    
    # Jobs
    pending_jobs: List[Job] = field(default_factory=list)
    
    # Stats
    total_submitted: int = 0
    total_completed: int = 0


@dataclass
class SchedulingDecision:
    """Решение о планировании"""
    job_id: str
    node_id: str
    decision_time: datetime = field(default_factory=datetime.now)
    
    # Metrics
    queue_wait_time_seconds: float = 0
    score: float = 0


class NodeSelector:
    """Селектор узлов"""
    
    def select_nodes(self, nodes: List[Node], job: Job) -> List[Node]:
        """Выбор подходящих узлов"""
        candidates = []
        
        for node in nodes:
            if not node.healthy or not node.schedulable:
                continue
                
            # Check resource availability
            if not node.available_capacity.can_fit(job.resource_request):
                continue
                
            # Check node selector
            if job.node_selector:
                match = all(
                    node.labels.get(k) == v
                    for k, v in job.node_selector.items()
                )
                if not match:
                    continue
                    
            candidates.append(node)
            
        return candidates


class NodeScorer:
    """Скорер узлов"""
    
    def score(self, node: Node, job: Job) -> float:
        """Расчёт оценки узла"""
        score = 0.0
        
        # Resource efficiency
        available = node.available_capacity
        request = job.resource_request
        
        if available.cpu_cores > 0:
            cpu_utilization = request.cpu_cores / available.cpu_cores
            score += (1 - cpu_utilization) * 30
            
        if available.memory_mb > 0:
            memory_utilization = request.memory_mb / available.memory_mb
            score += (1 - memory_utilization) * 30
            
        # Balance (prefer nodes with fewer jobs)
        job_count = len(node.running_jobs)
        score += max(0, 20 - job_count)
        
        # Affinity bonus
        if job.node_selector:
            matched = sum(1 for k, v in job.node_selector.items() 
                         if node.labels.get(k) == v)
            score += matched * 10
            
        return score


class Scheduler:
    """Планировщик"""
    
    def __init__(self):
        self.selector = NodeSelector()
        self.scorer = NodeScorer()
        
    def schedule(self, job: Job, nodes: List[Node]) -> Optional[SchedulingDecision]:
        """Планирование задачи"""
        # Filter nodes
        candidates = self.selector.select_nodes(nodes, job)
        
        if not candidates:
            return None
            
        # Score nodes
        scored = [(self.scorer.score(node, job), node) for node in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Select best node
        best_score, best_node = scored[0]
        
        wait_time = (datetime.now() - job.created_at).total_seconds()
        
        return SchedulingDecision(
            job_id=job.job_id,
            node_id=best_node.node_id,
            queue_wait_time_seconds=wait_time,
            score=best_score
        )


class QueueManager:
    """Менеджер очередей"""
    
    def __init__(self):
        self.queues: Dict[str, Queue] = {}
        self._default_queue: Optional[str] = None
        
    def create_queue(self, name: str, policy: SchedulingPolicy = SchedulingPolicy.FIFO,
                    max_jobs: int = 100, weight: int = 1) -> Queue:
        """Создание очереди"""
        queue = Queue(
            queue_id=f"queue_{uuid.uuid4().hex[:8]}",
            name=name,
            policy=policy,
            max_jobs=max_jobs,
            weight=weight
        )
        self.queues[queue.queue_id] = queue
        
        if self._default_queue is None:
            self._default_queue = queue.queue_id
            
        return queue
        
    def submit_job(self, job: Job, queue_id: Optional[str] = None) -> bool:
        """Отправка задачи в очередь"""
        q_id = queue_id or self._default_queue
        if not q_id or q_id not in self.queues:
            return False
            
        queue = self.queues[q_id]
        
        if len(queue.pending_jobs) >= queue.max_jobs:
            return False
            
        if queue.policy == SchedulingPolicy.PRIORITY:
            heapq.heappush(queue.pending_jobs, job)
        else:
            queue.pending_jobs.append(job)
            
        queue.total_submitted += 1
        return True
        
    def get_next_job(self, queue_id: str) -> Optional[Job]:
        """Получение следующей задачи"""
        if queue_id not in self.queues:
            return None
            
        queue = self.queues[queue_id]
        
        if not queue.pending_jobs:
            return None
            
        if queue.policy == SchedulingPolicy.PRIORITY:
            return heapq.heappop(queue.pending_jobs)
        else:
            return queue.pending_jobs.pop(0)


class ResourceSchedulerPlatform:
    """Платформа планирования ресурсов"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.jobs: Dict[str, Job] = {}
        self.scheduler = Scheduler()
        self.queue_manager = QueueManager()
        self.decisions: List[SchedulingDecision] = []
        
    def add_node(self, name: str, cpu_cores: float = 4, memory_mb: int = 8192,
                gpu_units: int = 0, labels: Dict[str, str] = None) -> Node:
        """Добавление узла"""
        node = Node(
            node_id=f"node_{uuid.uuid4().hex[:8]}",
            name=name,
            total_capacity=ResourceCapacity(
                cpu_cores=cpu_cores,
                memory_mb=memory_mb,
                gpu_units=gpu_units,
                storage_gb=100
            ),
            labels=labels or {}
        )
        self.nodes[node.node_id] = node
        return node
        
    def create_job(self, name: str, cpu_cores: float = 0.5, memory_mb: int = 512,
                  priority: JobPriority = JobPriority.MEDIUM,
                  node_selector: Dict[str, str] = None) -> Job:
        """Создание задачи"""
        job = Job(
            job_id=f"job_{uuid.uuid4().hex[:8]}",
            name=name,
            resource_request=ResourceRequest(
                cpu_cores=cpu_cores,
                memory_mb=memory_mb
            ),
            priority=priority,
            node_selector=node_selector or {}
        )
        self.jobs[job.job_id] = job
        return job
        
    async def schedule_job(self, job: Job) -> bool:
        """Планирование задачи"""
        nodes_list = list(self.nodes.values())
        decision = self.scheduler.schedule(job, nodes_list)
        
        if not decision:
            return False
            
        # Update job
        job.status = JobStatus.SCHEDULED
        job.assigned_node = decision.node_id
        job.scheduled_at = datetime.now()
        
        # Update node
        node = self.nodes[decision.node_id]
        node.running_jobs.append(job.job_id)
        node.allocated_capacity.cpu_cores += job.resource_request.cpu_cores
        node.allocated_capacity.memory_mb += job.resource_request.memory_mb
        
        self.decisions.append(decision)
        
        return True
        
    async def run_job(self, job_id: str) -> bool:
        """Запуск задачи"""
        job = self.jobs.get(job_id)
        if not job or job.status != JobStatus.SCHEDULED:
            return False
            
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        # Simulate execution
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        
        # Release resources
        if job.assigned_node:
            node = self.nodes.get(job.assigned_node)
            if node and job.job_id in node.running_jobs:
                node.running_jobs.remove(job.job_id)
                node.allocated_capacity.cpu_cores -= job.resource_request.cpu_cores
                node.allocated_capacity.memory_mb -= job.resource_request.memory_mb
                
        return True
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        completed = len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED])
        running = len([j for j in self.jobs.values() if j.status == JobStatus.RUNNING])
        pending = len([j for j in self.jobs.values() if j.status == JobStatus.PENDING])
        
        total_cpu = sum(n.total_capacity.cpu_cores for n in self.nodes.values())
        used_cpu = sum(n.allocated_capacity.cpu_cores for n in self.nodes.values())
        
        return {
            "total_nodes": len(self.nodes),
            "total_jobs": len(self.jobs),
            "completed_jobs": completed,
            "running_jobs": running,
            "pending_jobs": pending,
            "cpu_utilization": (used_cpu / total_cpu * 100) if total_cpu > 0 else 0,
            "scheduling_decisions": len(self.decisions)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 207: Resource Scheduler Platform")
    print("=" * 60)
    
    platform = ResourceSchedulerPlatform()
    print("✓ Resource Scheduler Platform created")
    
    # Add nodes
    print("\n🖥️ Adding Cluster Nodes...")
    
    nodes_config = [
        ("node-01", 8, 16384, 2, {"zone": "us-east-1a", "type": "compute"}),
        ("node-02", 4, 8192, 0, {"zone": "us-east-1b", "type": "general"}),
        ("node-03", 16, 32768, 4, {"zone": "us-east-1a", "type": "gpu"}),
        ("node-04", 4, 8192, 0, {"zone": "us-east-1c", "type": "general"}),
        ("node-05", 8, 16384, 0, {"zone": "us-east-1b", "type": "compute"}),
    ]
    
    for name, cpu, mem, gpu, labels in nodes_config:
        node = platform.add_node(name, cpu, mem, gpu, labels)
        print(f"  ✓ {name}: {cpu} CPU, {mem}MB RAM, {gpu} GPU")
        
    # Create queues
    print("\n📋 Creating Job Queues...")
    
    default_queue = platform.queue_manager.create_queue(
        "default", SchedulingPolicy.FIFO, max_jobs=50
    )
    print(f"  ✓ Default queue (FIFO)")
    
    priority_queue = platform.queue_manager.create_queue(
        "priority", SchedulingPolicy.PRIORITY, max_jobs=100, weight=2
    )
    print(f"  ✓ Priority queue")
    
    # Create and schedule jobs
    print("\n📦 Creating and Scheduling Jobs...")
    
    jobs_config = [
        ("data-processing", 2, 4096, JobPriority.HIGH, {}),
        ("web-server", 0.5, 512, JobPriority.MEDIUM, {"type": "general"}),
        ("ml-training", 4, 8192, JobPriority.HIGH, {"type": "gpu"}),
        ("batch-job", 1, 2048, JobPriority.LOW, {}),
        ("api-backend", 1, 1024, JobPriority.MEDIUM, {"zone": "us-east-1a"}),
        ("analytics", 2, 4096, JobPriority.MEDIUM, {"type": "compute"}),
        ("worker", 0.5, 256, JobPriority.LOW, {}),
        ("report-gen", 1, 2048, JobPriority.HIGH, {}),
    ]
    
    for name, cpu, mem, priority, selector in jobs_config:
        job = platform.create_job(name, cpu, mem, priority, selector)
        scheduled = await platform.schedule_job(job)
        status = "✓" if scheduled else "○"
        print(f"  {status} {name} [{priority.name}] -> {job.assigned_node or 'pending'}")
        
    # Run jobs
    print("\n🚀 Running Jobs...")
    
    for job in list(platform.jobs.values()):
        if job.status == JobStatus.SCHEDULED:
            await platform.run_job(job.job_id)
            duration = (job.completed_at - job.started_at).total_seconds() * 1000
            print(f"  ✓ {job.name}: completed in {duration:.0f}ms")
            
    # Display node utilization
    print("\n📊 Node Utilization:")
    
    print("\n  ┌──────────────┬────────────┬────────────┬───────────┬───────────┐")
    print("  │ Node         │ CPU Used   │ Memory     │ GPU       │ Jobs      │")
    print("  ├──────────────┼────────────┼────────────┼───────────┼───────────┤")
    
    for node in platform.nodes.values():
        name = node.name[:12].ljust(12)
        cpu_pct = (node.allocated_capacity.cpu_cores / node.total_capacity.cpu_cores * 100) if node.total_capacity.cpu_cores > 0 else 0
        mem_pct = (node.allocated_capacity.memory_mb / node.total_capacity.memory_mb * 100) if node.total_capacity.memory_mb > 0 else 0
        gpu_str = f"{node.allocated_capacity.gpu_units}/{node.total_capacity.gpu_units}".center(9)
        jobs = str(len(node.running_jobs)).center(9)
        
        cpu_str = f"{cpu_pct:.0f}%".center(10)
        mem_str = f"{mem_pct:.0f}%".center(10)
        
        print(f"  │ {name} │ {cpu_str} │ {mem_str} │ {gpu_str} │ {jobs} │")
        
    print("  └──────────────┴────────────┴────────────┴───────────┴───────────┘")
    
    # Job status summary
    print("\n📦 Job Status Summary:")
    
    status_counts = {}
    for job in platform.jobs.values():
        s = job.status.value
        status_counts[s] = status_counts.get(s, 0) + 1
        
    for status, count in status_counts.items():
        bar = "█" * count + "░" * (10 - count)
        print(f"  {status.capitalize():12s} [{bar}] {count}")
        
    # Priority distribution
    print("\n📊 Priority Distribution:")
    
    priority_counts = {}
    for job in platform.jobs.values():
        p = job.priority.name
        priority_counts[p] = priority_counts.get(p, 0) + 1
        
    for priority, count in priority_counts.items():
        bar = "█" * count
        print(f"  {priority:8s} {bar} ({count})")
        
    # Scheduling decisions analysis
    print("\n⏱️ Scheduling Performance:")
    
    if platform.decisions:
        wait_times = [d.queue_wait_time_seconds for d in platform.decisions]
        scores = [d.score for d in platform.decisions]
        
        print(f"\n  Queue Wait Time:")
        print(f"    Average: {sum(wait_times)/len(wait_times)*1000:.1f}ms")
        print(f"    Max: {max(wait_times)*1000:.1f}ms")
        
        print(f"\n  Scheduling Scores:")
        print(f"    Average: {sum(scores)/len(scores):.1f}")
        print(f"    Best: {max(scores):.1f}")
        
    # Node labels
    print("\n🏷️ Node Labels:")
    
    label_nodes = {}
    for node in platform.nodes.values():
        for key, value in node.labels.items():
            label = f"{key}={value}"
            if label not in label_nodes:
                label_nodes[label] = []
            label_nodes[label].append(node.name)
            
    for label, nodes in label_nodes.items():
        print(f"  {label}: {', '.join(nodes)}")
        
    # Resource allocation by zone
    print("\n🌍 Resources by Zone:")
    
    zone_resources = {}
    for node in platform.nodes.values():
        zone = node.labels.get("zone", "unknown")
        if zone not in zone_resources:
            zone_resources[zone] = {"cpu": 0, "memory": 0}
        zone_resources[zone]["cpu"] += node.total_capacity.cpu_cores
        zone_resources[zone]["memory"] += node.total_capacity.memory_mb
        
    for zone, resources in zone_resources.items():
        print(f"  {zone}: {resources['cpu']} CPU, {resources['memory']}MB RAM")
        
    # Queue statistics
    print("\n📋 Queue Statistics:")
    
    for queue in platform.queue_manager.queues.values():
        print(f"\n  {queue.name}:")
        print(f"    Policy: {queue.policy.value}")
        print(f"    Submitted: {queue.total_submitted}")
        print(f"    Pending: {len(queue.pending_jobs)}")
        print(f"    Weight: {queue.weight}")
        
    # Statistics
    stats = platform.get_statistics()
    
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Total Nodes: {stats['total_nodes']}")
    print(f"  Total Jobs: {stats['total_jobs']}")
    print(f"  Completed: {stats['completed_jobs']}")
    print(f"  Running: {stats['running_jobs']}")
    print(f"  Pending: {stats['pending_jobs']}")
    print(f"  CPU Utilization: {stats['cpu_utilization']:.1f}%")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                  Resource Scheduler Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Nodes:                   {stats['total_nodes']:>12}                        │")
    print(f"│ Total Jobs:                    {stats['total_jobs']:>12}                        │")
    print(f"│ Completed Jobs:                {stats['completed_jobs']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ CPU Utilization:                 {stats['cpu_utilization']:>10.1f}%                   │")
    print(f"│ Scheduling Decisions:          {stats['scheduling_decisions']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Resource Scheduler Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
