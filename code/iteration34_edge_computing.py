#!/usr/bin/env python3
"""
Server Init - Iteration 34: Edge Computing Platform
Распределённые вычисления на периферии сети

Функционал:
- Edge Node Management - управление периферийными узлами
- Edge-Cloud Sync - синхронизация edge-cloud
- Latency Optimization - оптимизация задержек
- Edge AI Inference - AI-инференс на edge
- Content Caching - кэширование контента
- Edge Security - безопасность периферии
- Bandwidth Management - управление пропускной способностью
- Edge Analytics - аналитика на edge
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random
import heapq
from collections import defaultdict
import threading
import math


class EdgeNodeStatus(Enum):
    """Статус edge-узла"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SYNCING = "syncing"
    OVERLOADED = "overloaded"


class EdgeNodeType(Enum):
    """Тип edge-узла"""
    COMPUTE = "compute"
    STORAGE = "storage"
    GATEWAY = "gateway"
    IOT_HUB = "iot_hub"
    CDN_POP = "cdn_pop"
    AI_ACCELERATOR = "ai_accelerator"


class SyncStrategy(Enum):
    """Стратегия синхронизации"""
    EVENTUAL = "eventual"
    STRONG = "strong"
    CAUSAL = "causal"
    SESSION = "session"
    BOUNDED_STALENESS = "bounded_staleness"


class CacheStrategy(Enum):
    """Стратегия кэширования"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"


@dataclass
class GeoLocation:
    """Геолокация"""
    latitude: float
    longitude: float
    region: str
    city: str
    country: str
    timezone: str = "UTC"


@dataclass
class EdgeNodeSpec:
    """Спецификация edge-узла"""
    cpu_cores: int
    memory_gb: float
    storage_gb: float
    gpu_units: int = 0
    network_bandwidth_mbps: int = 1000
    max_connections: int = 10000


@dataclass
class EdgeNode:
    """Edge-узел"""
    node_id: str
    name: str
    node_type: EdgeNodeType
    location: GeoLocation
    spec: EdgeNodeSpec
    status: EdgeNodeStatus = EdgeNodeStatus.OFFLINE
    parent_node: Optional[str] = None
    child_nodes: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Метрики
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    storage_usage: float = 0.0
    active_connections: int = 0
    requests_per_second: float = 0.0
    avg_latency_ms: float = 0.0
    
    # Состояние
    last_heartbeat: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    uptime_seconds: int = 0
    
    def is_healthy(self) -> bool:
        """Проверка здоровья узла"""
        if self.status not in [EdgeNodeStatus.ONLINE, EdgeNodeStatus.DEGRADED]:
            return False
        if (datetime.now() - self.last_heartbeat).seconds > 60:
            return False
        return True
    
    def get_capacity_score(self) -> float:
        """Получение оценки доступной ёмкости"""
        cpu_available = 1.0 - self.cpu_usage / 100
        mem_available = 1.0 - self.memory_usage / 100
        conn_available = 1.0 - self.active_connections / self.spec.max_connections
        return (cpu_available + mem_available + conn_available) / 3


@dataclass
class EdgeWorkload:
    """Рабочая нагрузка на edge"""
    workload_id: str
    name: str
    container_image: str
    cpu_request: float
    memory_request_mb: int
    replicas: int = 1
    gpu_required: bool = False
    latency_sla_ms: int = 100
    affinity_rules: Dict[str, Any] = field(default_factory=dict)
    deployed_nodes: List[str] = field(default_factory=list)


@dataclass
class CacheEntry:
    """Запись кэша"""
    key: str
    value: bytes
    size_bytes: int
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    origin: str = "unknown"
    content_type: str = "application/octet-stream"


@dataclass
class SyncOperation:
    """Операция синхронизации"""
    operation_id: str
    source_node: str
    target_node: str
    data_type: str
    data_size_bytes: int
    strategy: SyncStrategy
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress_percent: float = 0.0


class EdgeNodeManager:
    """Менеджер edge-узлов"""
    
    def __init__(self):
        self.nodes: Dict[str, EdgeNode] = {}
        self.node_hierarchy: Dict[str, List[str]] = {}  # parent -> children
        self.workloads: Dict[str, EdgeWorkload] = {}
        self.health_checks: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def register_node(self, node: EdgeNode) -> bool:
        """Регистрация edge-узла"""
        if node.node_id in self.nodes:
            return False
            
        self.nodes[node.node_id] = node
        
        # Обновление иерархии
        if node.parent_node:
            if node.parent_node not in self.node_hierarchy:
                self.node_hierarchy[node.parent_node] = []
            self.node_hierarchy[node.parent_node].append(node.node_id)
            
            # Обновление родительского узла
            if node.parent_node in self.nodes:
                self.nodes[node.parent_node].child_nodes.append(node.node_id)
                
        node.status = EdgeNodeStatus.ONLINE
        node.last_heartbeat = datetime.now()
        
        return True
        
    def deregister_node(self, node_id: str) -> bool:
        """Удаление регистрации узла"""
        if node_id not in self.nodes:
            return False
            
        node = self.nodes[node_id]
        
        # Переназначение дочерних узлов
        for child_id in node.child_nodes:
            if child_id in self.nodes:
                self.nodes[child_id].parent_node = node.parent_node
                
        # Удаление из иерархии
        if node.parent_node and node.parent_node in self.node_hierarchy:
            self.node_hierarchy[node.parent_node].remove(node_id)
            
        del self.nodes[node_id]
        return True
        
    def update_heartbeat(self, node_id: str, metrics: Dict[str, Any]) -> bool:
        """Обновление heartbeat узла"""
        if node_id not in self.nodes:
            return False
            
        node = self.nodes[node_id]
        node.last_heartbeat = datetime.now()
        
        # Обновление метрик
        if "cpu_usage" in metrics:
            node.cpu_usage = metrics["cpu_usage"]
        if "memory_usage" in metrics:
            node.memory_usage = metrics["memory_usage"]
        if "storage_usage" in metrics:
            node.storage_usage = metrics["storage_usage"]
        if "active_connections" in metrics:
            node.active_connections = metrics["active_connections"]
        if "requests_per_second" in metrics:
            node.requests_per_second = metrics["requests_per_second"]
        if "avg_latency_ms" in metrics:
            node.avg_latency_ms = metrics["avg_latency_ms"]
            
        # Проверка состояния
        self._check_node_health(node)
        
        return True
        
    def _check_node_health(self, node: EdgeNode):
        """Проверка здоровья узла"""
        issues = []
        
        if node.cpu_usage > 90:
            issues.append("high_cpu")
        if node.memory_usage > 90:
            issues.append("high_memory")
        if node.storage_usage > 95:
            issues.append("low_storage")
        if node.active_connections > node.spec.max_connections * 0.9:
            issues.append("connection_limit")
            
        if issues:
            if len(issues) >= 3:
                node.status = EdgeNodeStatus.OVERLOADED
            else:
                node.status = EdgeNodeStatus.DEGRADED
        else:
            node.status = EdgeNodeStatus.ONLINE
            
        # Сохранение истории проверок
        self.health_checks[node.node_id].append({
            "timestamp": datetime.now().isoformat(),
            "status": node.status.value,
            "issues": issues,
            "metrics": {
                "cpu": node.cpu_usage,
                "memory": node.memory_usage,
                "storage": node.storage_usage
            }
        })
        
        # Ограничение истории
        if len(self.health_checks[node.node_id]) > 1000:
            self.health_checks[node.node_id] = self.health_checks[node.node_id][-500:]
            
    def get_nodes_by_type(self, node_type: EdgeNodeType) -> List[EdgeNode]:
        """Получение узлов по типу"""
        return [n for n in self.nodes.values() if n.node_type == node_type]
        
    def get_nodes_by_region(self, region: str) -> List[EdgeNode]:
        """Получение узлов по региону"""
        return [n for n in self.nodes.values() if n.location.region == region]
        
    def get_healthy_nodes(self) -> List[EdgeNode]:
        """Получение здоровых узлов"""
        return [n for n in self.nodes.values() if n.is_healthy()]
        
    def find_nearest_node(self, location: GeoLocation, 
                          node_type: Optional[EdgeNodeType] = None) -> Optional[EdgeNode]:
        """Поиск ближайшего узла"""
        candidates = self.get_healthy_nodes()
        
        if node_type:
            candidates = [n for n in candidates if n.node_type == node_type]
            
        if not candidates:
            return None
            
        # Вычисление расстояния (упрощённо)
        def distance(node: EdgeNode) -> float:
            lat_diff = node.location.latitude - location.latitude
            lon_diff = node.location.longitude - location.longitude
            return math.sqrt(lat_diff**2 + lon_diff**2)
            
        return min(candidates, key=distance)


class EdgeCloudSync:
    """Синхронизация Edge-Cloud"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.operations: Dict[str, SyncOperation] = {}
        self.sync_queues: Dict[str, List[SyncOperation]] = defaultdict(list)
        self.conflict_handlers: Dict[str, Callable] = {}
        self.vector_clocks: Dict[str, Dict[str, int]] = defaultdict(dict)
        
    def create_sync_operation(self, source_node: str, target_node: str,
                               data_type: str, data_size: int,
                               strategy: SyncStrategy) -> SyncOperation:
        """Создание операции синхронизации"""
        operation = SyncOperation(
            operation_id=f"sync_{int(time.time()*1000)}_{random.randint(1000,9999)}",
            source_node=source_node,
            target_node=target_node,
            data_type=data_type,
            data_size_bytes=data_size,
            strategy=strategy
        )
        
        self.operations[operation.operation_id] = operation
        self.sync_queues[target_node].append(operation)
        
        return operation
        
    async def execute_sync(self, operation: SyncOperation) -> bool:
        """Выполнение синхронизации"""
        operation.status = "in_progress"
        operation.started_at = datetime.now()
        
        try:
            # Проверка узлов
            source = self.node_manager.nodes.get(operation.source_node)
            target = self.node_manager.nodes.get(operation.target_node)
            
            if not source or not target:
                raise ValueError("Source or target node not found")
                
            if not source.is_healthy() or not target.is_healthy():
                raise ValueError("Unhealthy nodes cannot sync")
                
            # Симуляция синхронизации по стратегии
            if operation.strategy == SyncStrategy.STRONG:
                await self._strong_sync(operation, source, target)
            elif operation.strategy == SyncStrategy.EVENTUAL:
                await self._eventual_sync(operation, source, target)
            elif operation.strategy == SyncStrategy.CAUSAL:
                await self._causal_sync(operation, source, target)
            else:
                await self._default_sync(operation, source, target)
                
            operation.status = "completed"
            operation.completed_at = datetime.now()
            operation.progress_percent = 100.0
            
            # Обновление времени синхронизации узлов
            source.last_sync = datetime.now()
            target.last_sync = datetime.now()
            
            return True
            
        except Exception as e:
            operation.status = "failed"
            operation.error = str(e)
            return False
            
    async def _strong_sync(self, op: SyncOperation, source: EdgeNode, target: EdgeNode):
        """Строгая консистентность"""
        # Двухфазный коммит
        chunks = max(1, op.data_size_bytes // 1024)
        
        # Фаза 1: Подготовка
        for i in range(chunks):
            await asyncio.sleep(0.01)  # Симуляция передачи
            op.progress_percent = (i / chunks) * 50
            
        # Фаза 2: Коммит
        for i in range(chunks):
            await asyncio.sleep(0.005)
            op.progress_percent = 50 + (i / chunks) * 50
            
    async def _eventual_sync(self, op: SyncOperation, source: EdgeNode, target: EdgeNode):
        """Eventual consistency"""
        chunks = max(1, op.data_size_bytes // 1024)
        
        for i in range(chunks):
            await asyncio.sleep(0.005)
            op.progress_percent = (i / chunks) * 100
            
    async def _causal_sync(self, op: SyncOperation, source: EdgeNode, target: EdgeNode):
        """Каузальная консистентность"""
        # Обновление vector clock
        if source.node_id not in self.vector_clocks[op.data_type]:
            self.vector_clocks[op.data_type][source.node_id] = 0
            
        self.vector_clocks[op.data_type][source.node_id] += 1
        
        chunks = max(1, op.data_size_bytes // 1024)
        
        for i in range(chunks):
            await asyncio.sleep(0.007)
            op.progress_percent = (i / chunks) * 100
            
    async def _default_sync(self, op: SyncOperation, source: EdgeNode, target: EdgeNode):
        """Синхронизация по умолчанию"""
        chunks = max(1, op.data_size_bytes // 1024)
        
        for i in range(chunks):
            await asyncio.sleep(0.005)
            op.progress_percent = (i / chunks) * 100
            
    def register_conflict_handler(self, data_type: str, handler: Callable):
        """Регистрация обработчика конфликтов"""
        self.conflict_handlers[data_type] = handler
        
    def resolve_conflict(self, data_type: str, local_data: Any, 
                         remote_data: Any, local_timestamp: datetime,
                         remote_timestamp: datetime) -> Any:
        """Разрешение конфликта"""
        if data_type in self.conflict_handlers:
            return self.conflict_handlers[data_type](
                local_data, remote_data, local_timestamp, remote_timestamp
            )
            
        # По умолчанию - последний выигрывает
        if remote_timestamp > local_timestamp:
            return remote_data
        return local_data


class LatencyOptimizer:
    """Оптимизатор задержек"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.latency_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.routing_cache: Dict[str, str] = {}
        self.measurements: Dict[str, List[float]] = defaultdict(list)
        
    def record_latency(self, source: str, target: str, latency_ms: float):
        """Запись измерения задержки"""
        key = f"{source}:{target}"
        self.measurements[key].append(latency_ms)
        
        # Ограничение истории
        if len(self.measurements[key]) > 100:
            self.measurements[key] = self.measurements[key][-50:]
            
        # Обновление матрицы
        self.latency_matrix[source][target] = sum(self.measurements[key]) / len(self.measurements[key])
        
    def get_optimal_route(self, source: str, target: str) -> List[str]:
        """Получение оптимального маршрута (Dijkstra)"""
        if source not in self.node_manager.nodes or target not in self.node_manager.nodes:
            return []
            
        # Dijkstra's algorithm
        distances = {node_id: float('inf') for node_id in self.node_manager.nodes}
        distances[source] = 0
        predecessors = {}
        visited = set()
        
        heap = [(0, source)]
        
        while heap:
            current_dist, current = heapq.heappop(heap)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            if current == target:
                break
                
            # Соседи - узлы с известной задержкой
            for neighbor in self.latency_matrix.get(current, {}):
                if neighbor in visited:
                    continue
                    
                latency = self.latency_matrix[current].get(neighbor, float('inf'))
                new_dist = current_dist + latency
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current
                    heapq.heappush(heap, (new_dist, neighbor))
                    
        # Построение пути
        if target not in predecessors and source != target:
            return []
            
        path = []
        current = target
        while current != source:
            path.append(current)
            current = predecessors.get(current)
            if current is None:
                return []
        path.append(source)
        
        return list(reversed(path))
        
    def select_optimal_node(self, client_location: GeoLocation,
                            workload_requirements: Dict[str, Any]) -> Optional[str]:
        """Выбор оптимального узла для клиента"""
        candidates = []
        
        for node in self.node_manager.get_healthy_nodes():
            # Проверка требований
            if workload_requirements.get("gpu") and node.spec.gpu_units == 0:
                continue
            if workload_requirements.get("min_memory_gb", 0) > node.spec.memory_gb:
                continue
                
            # Оценка узла
            score = self._calculate_node_score(node, client_location, workload_requirements)
            candidates.append((score, node.node_id))
            
        if not candidates:
            return None
            
        # Возврат лучшего узла
        candidates.sort(reverse=True)
        return candidates[0][1]
        
    def _calculate_node_score(self, node: EdgeNode, client_location: GeoLocation,
                               requirements: Dict[str, Any]) -> float:
        """Расчёт оценки узла"""
        score = 0.0
        
        # Фактор близости (30%)
        lat_diff = abs(node.location.latitude - client_location.latitude)
        lon_diff = abs(node.location.longitude - client_location.longitude)
        distance = math.sqrt(lat_diff**2 + lon_diff**2)
        proximity_score = max(0, 1 - distance / 180) * 0.3
        score += proximity_score
        
        # Фактор доступности ресурсов (40%)
        capacity_score = node.get_capacity_score() * 0.4
        score += capacity_score
        
        # Фактор задержки (30%)
        if node.avg_latency_ms > 0:
            latency_sla = requirements.get("latency_sla_ms", 100)
            latency_score = max(0, 1 - node.avg_latency_ms / latency_sla) * 0.3
            score += latency_score
        else:
            score += 0.15  # Нет данных - средняя оценка
            
        return score


class EdgeAIInference:
    """AI-инференс на edge"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.models: Dict[str, Dict[str, Any]] = {}
        self.deployed_models: Dict[str, Set[str]] = defaultdict(set)  # node_id -> model_ids
        self.inference_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
    def register_model(self, model_id: str, model_info: Dict[str, Any]) -> bool:
        """Регистрация AI-модели"""
        self.models[model_id] = {
            "id": model_id,
            "name": model_info.get("name", model_id),
            "type": model_info.get("type", "generic"),
            "size_mb": model_info.get("size_mb", 100),
            "memory_required_mb": model_info.get("memory_required_mb", 256),
            "gpu_required": model_info.get("gpu_required", False),
            "quantized": model_info.get("quantized", False),
            "input_format": model_info.get("input_format", "tensor"),
            "output_format": model_info.get("output_format", "tensor"),
            "registered_at": datetime.now().isoformat()
        }
        return True
        
    def deploy_model_to_node(self, model_id: str, node_id: str) -> bool:
        """Развёртывание модели на узел"""
        if model_id not in self.models:
            return False
            
        node = self.node_manager.nodes.get(node_id)
        if not node:
            return False
            
        model = self.models[model_id]
        
        # Проверка ресурсов
        if model["gpu_required"] and node.spec.gpu_units == 0:
            return False
            
        available_memory = node.spec.memory_gb * 1024 * (1 - node.memory_usage / 100)
        if available_memory < model["memory_required_mb"]:
            return False
            
        # Развёртывание
        self.deployed_models[node_id].add(model_id)
        
        return True
        
    def undeploy_model(self, model_id: str, node_id: str) -> bool:
        """Удаление модели с узла"""
        if model_id in self.deployed_models.get(node_id, set()):
            self.deployed_models[node_id].remove(model_id)
            return True
        return False
        
    async def run_inference(self, model_id: str, node_id: str, 
                            input_data: Any) -> Dict[str, Any]:
        """Выполнение инференса"""
        start_time = time.time()
        
        if model_id not in self.deployed_models.get(node_id, set()):
            return {"error": "Model not deployed on this node"}
            
        node = self.node_manager.nodes.get(node_id)
        if not node or not node.is_healthy():
            return {"error": "Node unhealthy or not found"}
            
        # Симуляция инференса
        model = self.models[model_id]
        
        # Время зависит от размера модели и нагрузки узла
        base_time = model["size_mb"] / 1000  # Базовое время
        load_factor = 1 + node.cpu_usage / 100  # Фактор нагрузки
        inference_time = base_time * load_factor
        
        await asyncio.sleep(inference_time)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Обновление статистики
        if model_id not in self.inference_stats[node_id]:
            self.inference_stats[node_id][model_id] = {
                "total_requests": 0,
                "total_time_ms": 0,
                "avg_time_ms": 0
            }
            
        stats = self.inference_stats[node_id][model_id]
        stats["total_requests"] += 1
        stats["total_time_ms"] += elapsed_ms
        stats["avg_time_ms"] = stats["total_time_ms"] / stats["total_requests"]
        
        return {
            "model_id": model_id,
            "node_id": node_id,
            "inference_time_ms": elapsed_ms,
            "output": f"inference_result_{int(time.time())}",
            "success": True
        }
        
    def get_best_inference_node(self, model_id: str) -> Optional[str]:
        """Получение лучшего узла для инференса"""
        if model_id not in self.models:
            return None
            
        candidates = []
        
        for node_id, models in self.deployed_models.items():
            if model_id not in models:
                continue
                
            node = self.node_manager.nodes.get(node_id)
            if not node or not node.is_healthy():
                continue
                
            # Оценка: меньше нагрузка = лучше
            score = node.get_capacity_score()
            
            # Бонус за GPU
            if node.spec.gpu_units > 0:
                score += 0.3
                
            candidates.append((score, node_id))
            
        if not candidates:
            return None
            
        candidates.sort(reverse=True)
        return candidates[0][1]


class EdgeContentCache:
    """Кэширование контента на edge"""
    
    def __init__(self, max_size_mb: int = 1024):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.entries: Dict[str, CacheEntry] = {}
        self.strategy = CacheStrategy.LRU
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        
    def set_strategy(self, strategy: CacheStrategy):
        """Установка стратегии кэширования"""
        self.strategy = strategy
        
    def get(self, key: str) -> Optional[bytes]:
        """Получение из кэша"""
        entry = self.entries.get(key)
        
        if not entry:
            self.miss_count += 1
            return None
            
        # Проверка срока действия
        if entry.expires_at and datetime.now() > entry.expires_at:
            self._remove(key)
            self.miss_count += 1
            return None
            
        # Обновление статистики доступа
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        
        self.hit_count += 1
        return entry.value
        
    def put(self, key: str, value: bytes, ttl_seconds: Optional[int] = None,
            origin: str = "unknown", content_type: str = "application/octet-stream"):
        """Добавление в кэш"""
        size = len(value)
        
        # Если запись уже существует - удаляем
        if key in self.entries:
            self._remove(key)
            
        # Освобождение места
        while self.current_size + size > self.max_size_bytes:
            if not self._evict():
                return False  # Не удалось освободить место
                
        # Создание записи
        entry = CacheEntry(
            key=key,
            value=value,
            size_bytes=size,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
            origin=origin,
            content_type=content_type
        )
        
        self.entries[key] = entry
        self.current_size += size
        
        return True
        
    def _remove(self, key: str):
        """Удаление записи"""
        if key in self.entries:
            entry = self.entries[key]
            self.current_size -= entry.size_bytes
            del self.entries[key]
            
    def _evict(self) -> bool:
        """Вытеснение записи"""
        if not self.entries:
            return False
            
        victim_key = None
        
        if self.strategy == CacheStrategy.LRU:
            victim_key = min(self.entries, key=lambda k: self.entries[k].last_accessed)
        elif self.strategy == CacheStrategy.LFU:
            victim_key = min(self.entries, key=lambda k: self.entries[k].access_count)
        elif self.strategy == CacheStrategy.FIFO:
            victim_key = min(self.entries, key=lambda k: self.entries[k].created_at)
        elif self.strategy == CacheStrategy.TTL:
            # Вытесняем тех, у кого скоро истекает TTL
            ttl_entries = [(k, e.expires_at) for k, e in self.entries.items() if e.expires_at]
            if ttl_entries:
                victim_key = min(ttl_entries, key=lambda x: x[1])[0]
            else:
                victim_key = min(self.entries, key=lambda k: self.entries[k].created_at)
        else:
            victim_key = next(iter(self.entries))
            
        if victim_key:
            self._remove(victim_key)
            self.eviction_count += 1
            return True
            
        return False
        
    def invalidate(self, key: str) -> bool:
        """Инвалидация записи"""
        if key in self.entries:
            self._remove(key)
            return True
        return False
        
    def invalidate_by_prefix(self, prefix: str) -> int:
        """Инвалидация записей по префиксу"""
        keys_to_remove = [k for k in self.entries if k.startswith(prefix)]
        for key in keys_to_remove:
            self._remove(key)
        return len(keys_to_remove)
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "entries_count": len(self.entries),
            "current_size_mb": self.current_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "utilization": self.current_size / self.max_size_bytes,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "eviction_count": self.eviction_count,
            "strategy": self.strategy.value
        }


class EdgeSecurity:
    """Безопасность edge"""
    
    def __init__(self):
        self.trusted_nodes: Set[str] = set()
        self.node_certificates: Dict[str, Dict[str, Any]] = {}
        self.access_policies: Dict[str, Dict[str, Any]] = {}
        self.security_events: List[Dict[str, Any]] = []
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "requests": 0,
            "window_start": datetime.now(),
            "limit": 1000,
            "window_seconds": 60
        })
        
    def register_trusted_node(self, node_id: str, certificate: Dict[str, Any]) -> bool:
        """Регистрация доверенного узла"""
        # Валидация сертификата
        if not self._validate_certificate(certificate):
            self._log_security_event("certificate_validation_failed", node_id)
            return False
            
        self.trusted_nodes.add(node_id)
        self.node_certificates[node_id] = certificate
        
        return True
        
    def _validate_certificate(self, certificate: Dict[str, Any]) -> bool:
        """Валидация сертификата"""
        required_fields = ["subject", "issuer", "valid_from", "valid_until", "public_key"]
        
        for field in required_fields:
            if field not in certificate:
                return False
                
        # Проверка срока действия
        valid_until = datetime.fromisoformat(certificate["valid_until"])
        if datetime.now() > valid_until:
            return False
            
        return True
        
    def authenticate_node(self, node_id: str, token: str) -> bool:
        """Аутентификация узла"""
        if node_id not in self.trusted_nodes:
            self._log_security_event("untrusted_node_access", node_id)
            return False
            
        # Проверка токена (упрощённо)
        expected_hash = hashlib.sha256(
            f"{node_id}:{self.node_certificates[node_id].get('public_key', '')}".encode()
        ).hexdigest()[:32]
        
        if token != expected_hash:
            self._log_security_event("invalid_token", node_id)
            return False
            
        return True
        
    def check_rate_limit(self, client_id: str) -> bool:
        """Проверка rate limit"""
        rate_info = self.rate_limits[client_id]
        
        # Сброс окна при необходимости
        elapsed = (datetime.now() - rate_info["window_start"]).seconds
        if elapsed >= rate_info["window_seconds"]:
            rate_info["requests"] = 0
            rate_info["window_start"] = datetime.now()
            
        # Проверка лимита
        if rate_info["requests"] >= rate_info["limit"]:
            self._log_security_event("rate_limit_exceeded", client_id)
            return False
            
        rate_info["requests"] += 1
        return True
        
    def set_rate_limit(self, client_id: str, limit: int, window_seconds: int = 60):
        """Установка rate limit"""
        self.rate_limits[client_id]["limit"] = limit
        self.rate_limits[client_id]["window_seconds"] = window_seconds
        
    def create_access_policy(self, policy_id: str, policy: Dict[str, Any]) -> bool:
        """Создание политики доступа"""
        self.access_policies[policy_id] = {
            "id": policy_id,
            "name": policy.get("name", policy_id),
            "resources": policy.get("resources", []),
            "actions": policy.get("actions", []),
            "conditions": policy.get("conditions", {}),
            "effect": policy.get("effect", "allow"),
            "created_at": datetime.now().isoformat()
        }
        return True
        
    def check_access(self, node_id: str, resource: str, action: str) -> bool:
        """Проверка доступа"""
        for policy in self.access_policies.values():
            if self._policy_matches(policy, node_id, resource, action):
                if policy["effect"] == "allow":
                    return True
                elif policy["effect"] == "deny":
                    self._log_security_event("access_denied_by_policy", node_id, {
                        "resource": resource,
                        "action": action,
                        "policy": policy["id"]
                    })
                    return False
                    
        # По умолчанию - запрет
        return False
        
    def _policy_matches(self, policy: Dict[str, Any], node_id: str, 
                        resource: str, action: str) -> bool:
        """Проверка соответствия политике"""
        # Проверка ресурсов
        if policy["resources"] and resource not in policy["resources"]:
            if not any(r.endswith("*") and resource.startswith(r[:-1]) 
                      for r in policy["resources"]):
                return False
                
        # Проверка действий
        if policy["actions"] and action not in policy["actions"]:
            return False
            
        return True
        
    def _log_security_event(self, event_type: str, source: str, 
                            details: Optional[Dict[str, Any]] = None):
        """Логирование события безопасности"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "source": source,
            "details": details or {}
        }
        
        self.security_events.append(event)
        
        # Ограничение истории
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-5000:]
            
    def get_security_report(self) -> Dict[str, Any]:
        """Получение отчёта безопасности"""
        event_counts = defaultdict(int)
        for event in self.security_events:
            event_counts[event["type"]] += 1
            
        return {
            "trusted_nodes_count": len(self.trusted_nodes),
            "policies_count": len(self.access_policies),
            "total_events": len(self.security_events),
            "event_breakdown": dict(event_counts),
            "recent_events": self.security_events[-10:]
        }


class BandwidthManager:
    """Управление пропускной способностью"""
    
    def __init__(self):
        self.node_bandwidth: Dict[str, Dict[str, Any]] = {}
        self.traffic_classes: Dict[str, Dict[str, Any]] = {}
        self.allocations: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.usage_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def configure_node_bandwidth(self, node_id: str, total_bandwidth_mbps: int):
        """Конфигурация пропускной способности узла"""
        self.node_bandwidth[node_id] = {
            "total_mbps": total_bandwidth_mbps,
            "allocated_mbps": 0,
            "available_mbps": total_bandwidth_mbps,
            "current_usage_mbps": 0
        }
        
    def create_traffic_class(self, class_id: str, priority: int,
                             guaranteed_percent: float, max_percent: float):
        """Создание класса трафика"""
        self.traffic_classes[class_id] = {
            "id": class_id,
            "priority": priority,
            "guaranteed_percent": guaranteed_percent,
            "max_percent": max_percent
        }
        
    def allocate_bandwidth(self, node_id: str, traffic_class: str,
                           bandwidth_mbps: float) -> bool:
        """Выделение пропускной способности"""
        if node_id not in self.node_bandwidth:
            return False
            
        node = self.node_bandwidth[node_id]
        
        if bandwidth_mbps > node["available_mbps"]:
            return False
            
        self.allocations[node_id][traffic_class] = bandwidth_mbps
        node["allocated_mbps"] += bandwidth_mbps
        node["available_mbps"] -= bandwidth_mbps
        
        return True
        
    def release_bandwidth(self, node_id: str, traffic_class: str):
        """Освобождение пропускной способности"""
        if node_id not in self.allocations:
            return
            
        if traffic_class in self.allocations[node_id]:
            released = self.allocations[node_id][traffic_class]
            del self.allocations[node_id][traffic_class]
            
            if node_id in self.node_bandwidth:
                self.node_bandwidth[node_id]["allocated_mbps"] -= released
                self.node_bandwidth[node_id]["available_mbps"] += released
                
    def record_usage(self, node_id: str, traffic_class: str, usage_mbps: float):
        """Запись использования"""
        self.usage_history[node_id].append({
            "timestamp": datetime.now().isoformat(),
            "traffic_class": traffic_class,
            "usage_mbps": usage_mbps
        })
        
        # Ограничение истории
        if len(self.usage_history[node_id]) > 1000:
            self.usage_history[node_id] = self.usage_history[node_id][-500:]
            
        # Обновление текущего использования
        if node_id in self.node_bandwidth:
            total_usage = sum(
                h["usage_mbps"] for h in self.usage_history[node_id][-10:]
            ) / 10
            self.node_bandwidth[node_id]["current_usage_mbps"] = total_usage
            
    def get_bandwidth_report(self, node_id: str) -> Dict[str, Any]:
        """Получение отчёта о пропускной способности"""
        if node_id not in self.node_bandwidth:
            return {}
            
        node = self.node_bandwidth[node_id]
        allocations = self.allocations.get(node_id, {})
        
        return {
            "node_id": node_id,
            "total_bandwidth_mbps": node["total_mbps"],
            "allocated_mbps": node["allocated_mbps"],
            "available_mbps": node["available_mbps"],
            "current_usage_mbps": node["current_usage_mbps"],
            "utilization": node["current_usage_mbps"] / node["total_mbps"] if node["total_mbps"] > 0 else 0,
            "allocations": allocations,
            "traffic_classes": list(self.traffic_classes.keys())
        }


class EdgeAnalytics:
    """Аналитика на edge"""
    
    def __init__(self, node_manager: EdgeNodeManager):
        self.node_manager = node_manager
        self.metrics_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.aggregations: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
    def record_metric(self, node_id: str, metric_name: str, value: float,
                      labels: Optional[Dict[str, str]] = None):
        """Запись метрики"""
        self.metrics_buffer[node_id].append({
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
            "labels": labels or {}
        })
        
        # Ограничение буфера
        if len(self.metrics_buffer[node_id]) > 10000:
            self.metrics_buffer[node_id] = self.metrics_buffer[node_id][-5000:]
            
        # Проверка алертов
        self._check_alerts(node_id, metric_name, value)
        
    def create_alert_rule(self, rule_id: str, metric_name: str,
                          condition: str, threshold: float,
                          duration_seconds: int = 60):
        """Создание правила алерта"""
        self.alert_rules[rule_id] = {
            "id": rule_id,
            "metric": metric_name,
            "condition": condition,  # gt, lt, eq, ne
            "threshold": threshold,
            "duration_seconds": duration_seconds,
            "enabled": True,
            "last_triggered": None
        }
        
    def _check_alerts(self, node_id: str, metric_name: str, value: float):
        """Проверка алертов"""
        for rule_id, rule in self.alert_rules.items():
            if not rule["enabled"] or rule["metric"] != metric_name:
                continue
                
            triggered = False
            
            if rule["condition"] == "gt" and value > rule["threshold"]:
                triggered = True
            elif rule["condition"] == "lt" and value < rule["threshold"]:
                triggered = True
            elif rule["condition"] == "eq" and value == rule["threshold"]:
                triggered = True
            elif rule["condition"] == "ne" and value != rule["threshold"]:
                triggered = True
                
            if triggered:
                # Проверка cooldown
                if rule["last_triggered"]:
                    elapsed = (datetime.now() - datetime.fromisoformat(rule["last_triggered"])).seconds
                    if elapsed < rule["duration_seconds"]:
                        continue
                        
                self._fire_alert(rule_id, node_id, metric_name, value)
                rule["last_triggered"] = datetime.now().isoformat()
                
    def _fire_alert(self, rule_id: str, node_id: str, metric_name: str, value: float):
        """Создание алерта"""
        alert = {
            "id": f"alert_{int(time.time()*1000)}",
            "rule_id": rule_id,
            "node_id": node_id,
            "metric": metric_name,
            "value": value,
            "threshold": self.alert_rules[rule_id]["threshold"],
            "timestamp": datetime.now().isoformat(),
            "status": "firing"
        }
        
        self.alerts.append(alert)
        
        # Ограничение истории
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-500:]
            
    def aggregate_metrics(self, node_id: str, metric_name: str,
                          window_seconds: int = 300) -> Dict[str, Any]:
        """Агрегация метрик"""
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        
        values = [
            m["value"] for m in self.metrics_buffer.get(node_id, [])
            if m["metric"] == metric_name and 
               datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        if not values:
            return {"error": "No data"}
            
        return {
            "metric": metric_name,
            "node_id": node_id,
            "window_seconds": window_seconds,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
            "latest": values[-1]
        }
        
    def get_node_dashboard(self, node_id: str) -> Dict[str, Any]:
        """Получение дашборда узла"""
        node = self.node_manager.nodes.get(node_id)
        if not node:
            return {"error": "Node not found"}
            
        # Получение агрегаций основных метрик
        metrics = ["cpu_usage", "memory_usage", "requests_per_second", "latency_ms"]
        aggregations = {}
        
        for metric in metrics:
            aggregations[metric] = self.aggregate_metrics(node_id, metric)
            
        # Активные алерты
        active_alerts = [
            a for a in self.alerts
            if a["node_id"] == node_id and a["status"] == "firing"
        ]
        
        return {
            "node_id": node_id,
            "node_name": node.name,
            "status": node.status.value,
            "location": {
                "region": node.location.region,
                "city": node.location.city
            },
            "current_metrics": {
                "cpu_usage": node.cpu_usage,
                "memory_usage": node.memory_usage,
                "storage_usage": node.storage_usage,
                "active_connections": node.active_connections
            },
            "aggregations": aggregations,
            "active_alerts": len(active_alerts),
            "alerts": active_alerts[:5]
        }


class EdgeComputingPlatform:
    """Edge Computing платформа"""
    
    def __init__(self):
        self.node_manager = EdgeNodeManager()
        self.sync = EdgeCloudSync(self.node_manager)
        self.latency_optimizer = LatencyOptimizer(self.node_manager)
        self.ai_inference = EdgeAIInference(self.node_manager)
        self.content_cache = EdgeContentCache(max_size_mb=2048)
        self.security = EdgeSecurity()
        self.bandwidth = BandwidthManager()
        self.analytics = EdgeAnalytics(self.node_manager)
        
    def initialize(self):
        """Инициализация платформы"""
        # Создание классов трафика по умолчанию
        self.bandwidth.create_traffic_class("realtime", priority=1, 
                                            guaranteed_percent=30, max_percent=50)
        self.bandwidth.create_traffic_class("interactive", priority=2,
                                            guaranteed_percent=30, max_percent=40)
        self.bandwidth.create_traffic_class("background", priority=3,
                                            guaranteed_percent=10, max_percent=30)
                                            
        # Создание правил алертов по умолчанию
        self.analytics.create_alert_rule("high_cpu", "cpu_usage", "gt", 90)
        self.analytics.create_alert_rule("high_memory", "memory_usage", "gt", 90)
        self.analytics.create_alert_rule("high_latency", "latency_ms", "gt", 500)
        
        # Создание политик безопасности по умолчанию
        self.security.create_access_policy("default_allow", {
            "name": "Default Allow",
            "resources": ["data/*", "cache/*"],
            "actions": ["read"],
            "effect": "allow"
        })
        
    def deploy_node(self, node_config: Dict[str, Any]) -> Optional[EdgeNode]:
        """Развёртывание edge-узла"""
        node = EdgeNode(
            node_id=node_config.get("id", f"edge_{int(time.time())}"),
            name=node_config.get("name", "unnamed"),
            node_type=EdgeNodeType(node_config.get("type", "compute")),
            location=GeoLocation(
                latitude=node_config.get("latitude", 0),
                longitude=node_config.get("longitude", 0),
                region=node_config.get("region", "default"),
                city=node_config.get("city", "unknown"),
                country=node_config.get("country", "unknown")
            ),
            spec=EdgeNodeSpec(
                cpu_cores=node_config.get("cpu_cores", 4),
                memory_gb=node_config.get("memory_gb", 8),
                storage_gb=node_config.get("storage_gb", 100),
                gpu_units=node_config.get("gpu_units", 0),
                network_bandwidth_mbps=node_config.get("bandwidth_mbps", 1000)
            ),
            parent_node=node_config.get("parent_node"),
            tags=node_config.get("tags", {})
        )
        
        if self.node_manager.register_node(node):
            # Настройка пропускной способности
            self.bandwidth.configure_node_bandwidth(
                node.node_id, 
                node.spec.network_bandwidth_mbps
            )
            return node
            
        return None
        
    def get_platform_status(self) -> Dict[str, Any]:
        """Получение статуса платформы"""
        nodes = list(self.node_manager.nodes.values())
        healthy_nodes = [n for n in nodes if n.is_healthy()]
        
        return {
            "platform": "Edge Computing Platform v1.0",
            "nodes": {
                "total": len(nodes),
                "healthy": len(healthy_nodes),
                "by_type": {
                    t.value: len([n for n in nodes if n.node_type == t])
                    for t in EdgeNodeType
                },
                "by_status": {
                    s.value: len([n for n in nodes if n.status == s])
                    for s in EdgeNodeStatus
                }
            },
            "cache": self.content_cache.get_stats(),
            "security": {
                "trusted_nodes": len(self.security.trusted_nodes),
                "policies": len(self.security.access_policies)
            },
            "ai_models": {
                "registered": len(self.ai_inference.models),
                "deployed": sum(len(m) for m in self.ai_inference.deployed_models.values())
            },
            "sync_operations": {
                "total": len(self.sync.operations),
                "pending": len([o for o in self.sync.operations.values() if o.status == "pending"]),
                "in_progress": len([o for o in self.sync.operations.values() if o.status == "in_progress"])
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 34: Edge Computing Platform")
    print("=" * 60)
    
    # Создание платформы
    platform = EdgeComputingPlatform()
    platform.initialize()
    
    # Развёртывание узлов
    nodes_config = [
        {
            "id": "edge_eu_west_1",
            "name": "EU West Edge Node 1",
            "type": "compute",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "region": "eu-west",
            "city": "London",
            "country": "UK",
            "cpu_cores": 8,
            "memory_gb": 16,
            "storage_gb": 500,
            "bandwidth_mbps": 10000
        },
        {
            "id": "edge_us_east_1",
            "name": "US East Edge Node 1",
            "type": "compute",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "region": "us-east",
            "city": "New York",
            "country": "USA",
            "cpu_cores": 16,
            "memory_gb": 32,
            "storage_gb": 1000,
            "gpu_units": 2,
            "bandwidth_mbps": 25000
        },
        {
            "id": "edge_asia_1",
            "name": "Asia Pacific Edge Node 1",
            "type": "cdn_pop",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "region": "asia-pacific",
            "city": "Tokyo",
            "country": "Japan",
            "cpu_cores": 4,
            "memory_gb": 8,
            "storage_gb": 2000,
            "bandwidth_mbps": 40000
        }
    ]
    
    for config in nodes_config:
        node = platform.deploy_node(config)
        if node:
            print(f"✓ Deployed: {node.name} ({node.node_type.value})")
            
    # Регистрация AI-модели
    platform.ai_inference.register_model("yolo_v8", {
        "name": "YOLO v8 Object Detection",
        "type": "computer_vision",
        "size_mb": 250,
        "memory_required_mb": 512,
        "gpu_required": True
    })
    
    # Развёртывание модели
    if platform.ai_inference.deploy_model_to_node("yolo_v8", "edge_us_east_1"):
        print("✓ AI Model deployed to edge_us_east_1")
        
    # Кэширование контента
    platform.content_cache.put(
        "static/logo.png",
        b"PNG_IMAGE_DATA" * 1000,
        ttl_seconds=3600,
        content_type="image/png"
    )
    print(f"✓ Cache stats: {platform.content_cache.get_stats()['hit_rate']:.1%} hit rate")
    
    # Получение статуса
    status = platform.get_platform_status()
    print(f"\n📊 Platform Status:")
    print(f"   Total Nodes: {status['nodes']['total']}")
    print(f"   Healthy Nodes: {status['nodes']['healthy']}")
    print(f"   AI Models Deployed: {status['ai_models']['deployed']}")
    print(f"   Cache Size: {status['cache']['current_size_mb']:.2f} MB")
    
    print("\n" + "=" * 60)
    print("Edge Computing Platform initialized successfully!")
    print("=" * 60)
