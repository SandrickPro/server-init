#!/usr/bin/env python3
"""
Server Init - Iteration 35: Platform Engineering Automation
Автоматизация платформенной инженерии

Функционал:
- Self-Service Portal - портал самообслуживания
- Golden Paths - золотые пути разработки
- Internal Developer Platform (IDP) - внутренняя платформа разработчика
- Template Catalog - каталог шаблонов
- Environment Management - управление средами
- Service Catalog - каталог сервисов
- Cost Management - управление затратами
- Platform Analytics - аналитика платформы
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
from collections import defaultdict
import uuid


class TemplateType(Enum):
    """Тип шаблона"""
    MICROSERVICE = "microservice"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATA_PIPELINE = "data_pipeline"
    ML_MODEL = "ml_model"
    INFRASTRUCTURE = "infrastructure"
    LIBRARY = "library"
    DOCUMENTATION = "documentation"


class EnvironmentType(Enum):
    """Тип среды"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"
    TESTING = "testing"
    PREVIEW = "preview"


class ServiceTier(Enum):
    """Уровень сервиса"""
    TIER1_CRITICAL = "tier1_critical"
    TIER2_IMPORTANT = "tier2_important"
    TIER3_STANDARD = "tier3_standard"
    TIER4_EXPERIMENTAL = "tier4_experimental"


class RequestStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CostCategory(Enum):
    """Категория затрат"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    LICENSING = "licensing"
    OTHER = "other"


@dataclass
class Team:
    """Команда"""
    team_id: str
    name: str
    description: str
    owner_email: str
    members: List[str] = field(default_factory=list)
    cost_center: str = ""
    budget_monthly: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Template:
    """Шаблон проекта"""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    version: str
    repository_url: str
    
    # Конфигурация
    parameters: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    
    # Метаданные
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    documentation_url: str = ""
    
    # Статистика
    usage_count: int = 0
    last_used: Optional[datetime] = None
    rating: float = 0.0
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    included_resources: List[str] = field(default_factory=list)


@dataclass
class GoldenPath:
    """Золотой путь разработки"""
    path_id: str
    name: str
    description: str
    
    # Этапы пути
    stages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Шаблоны и инструменты
    recommended_templates: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    
    # Политики
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Метаданные
    target_audience: List[str] = field(default_factory=list)
    estimated_setup_time_hours: float = 1.0
    
    # Документация
    documentation: str = ""
    tutorials: List[str] = field(default_factory=list)


@dataclass
class Environment:
    """Среда развёртывания"""
    env_id: str
    name: str
    env_type: EnvironmentType
    team_id: str
    
    # Конфигурация
    cloud_provider: str = "aws"
    region: str = "us-east-1"
    cluster_name: str = ""
    namespace: str = ""
    
    # Ресурсы
    cpu_limit: float = 4.0
    memory_limit_gb: float = 8.0
    storage_limit_gb: float = 100.0
    
    # Состояние
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Затраты
    estimated_daily_cost: float = 0.0
    actual_monthly_cost: float = 0.0


@dataclass
class Service:
    """Сервис в каталоге"""
    service_id: str
    name: str
    description: str
    team_id: str
    
    # Классификация
    tier: ServiceTier = ServiceTier.TIER3_STANDARD
    category: str = "application"
    
    # Технические детали
    repository_url: str = ""
    documentation_url: str = ""
    api_docs_url: str = ""
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # SLA
    sla_availability: float = 99.9
    sla_latency_p99_ms: int = 500
    
    # Контакты
    oncall_team: str = ""
    slack_channel: str = ""
    
    # Состояние
    status: str = "active"
    last_deployment: Optional[datetime] = None
    version: str = "1.0.0"


@dataclass
class ServiceRequest:
    """Запрос на сервис"""
    request_id: str
    request_type: str  # create_project, provision_env, access_request, etc.
    requester_email: str
    team_id: str
    
    # Детали запроса
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Состояние
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Workflow
    approvers: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    rejected_by: Optional[str] = None
    rejection_reason: str = ""
    
    # Результат
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class CostRecord:
    """Запись о затратах"""
    record_id: str
    team_id: str
    service_id: str
    environment_id: str
    
    # Детали
    category: CostCategory
    amount: float
    currency: str = "USD"
    
    # Период
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Метаданные
    resource_type: str = ""
    resource_name: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


class TemplateCatalog:
    """Каталог шаблонов"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        
    def register_template(self, template: Template) -> bool:
        """Регистрация шаблона"""
        if template.template_id in self.templates:
            return False
            
        self.templates[template.template_id] = template
        self.categories[template.template_type.value].append(template.template_id)
        
        return True
        
    def get_template(self, template_id: str) -> Optional[Template]:
        """Получение шаблона"""
        return self.templates.get(template_id)
        
    def search_templates(self, query: str = "", 
                         template_type: Optional[TemplateType] = None,
                         tags: Optional[List[str]] = None) -> List[Template]:
        """Поиск шаблонов"""
        results = list(self.templates.values())
        
        if query:
            query_lower = query.lower()
            results = [t for t in results 
                      if query_lower in t.name.lower() or query_lower in t.description.lower()]
                      
        if template_type:
            results = [t for t in results if t.template_type == template_type]
            
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
            
        return sorted(results, key=lambda t: t.usage_count, reverse=True)
        
    def instantiate_template(self, template_id: str, 
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Создание проекта из шаблона"""
        template = self.templates.get(template_id)
        if not template:
            return {"error": "Template not found"}
            
        # Проверка обязательных параметров
        for param in template.required_params:
            if param not in parameters:
                return {"error": f"Missing required parameter: {param}"}
                
        # Объединение с defaults
        final_params = {**template.defaults, **parameters}
        
        # Обновление статистики
        template.usage_count += 1
        template.last_used = datetime.now()
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "parameters": final_params,
            "repository_url": template.repository_url,
            "resources": template.included_resources,
            "dependencies": template.dependencies,
            "created_at": datetime.now().isoformat()
        }
        
    def get_popular_templates(self, limit: int = 10) -> List[Template]:
        """Получение популярных шаблонов"""
        sorted_templates = sorted(
            self.templates.values(),
            key=lambda t: t.usage_count,
            reverse=True
        )
        return sorted_templates[:limit]


class GoldenPathManager:
    """Менеджер золотых путей"""
    
    def __init__(self, template_catalog: TemplateCatalog):
        self.template_catalog = template_catalog
        self.paths: Dict[str, GoldenPath] = {}
        self.user_progress: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
    def create_golden_path(self, path: GoldenPath) -> bool:
        """Создание золотого пути"""
        if path.path_id in self.paths:
            return False
            
        self.paths[path.path_id] = path
        return True
        
    def get_recommended_path(self, use_case: str, 
                             team_size: int,
                             tech_stack: List[str]) -> Optional[GoldenPath]:
        """Получение рекомендованного пути"""
        best_match = None
        best_score = 0
        
        for path in self.paths.values():
            score = 0
            
            # Проверка целевой аудитории
            if use_case in path.target_audience:
                score += 10
                
            # Проверка инструментов
            for tool in tech_stack:
                if tool in path.required_tools:
                    score += 2
                    
            # Оценка по времени настройки
            if team_size > 5 and path.estimated_setup_time_hours < 2:
                score += 5
                
            if score > best_score:
                best_score = score
                best_match = path
                
        return best_match
        
    def start_path(self, user_id: str, path_id: str) -> Dict[str, Any]:
        """Начало прохождения пути"""
        path = self.paths.get(path_id)
        if not path:
            return {"error": "Path not found"}
            
        self.user_progress[user_id][path_id] = {
            "started_at": datetime.now().isoformat(),
            "current_stage": 0,
            "completed_stages": [],
            "status": "in_progress"
        }
        
        return {
            "path_id": path_id,
            "path_name": path.name,
            "total_stages": len(path.stages),
            "current_stage": path.stages[0] if path.stages else None,
            "estimated_time_hours": path.estimated_setup_time_hours
        }
        
    def complete_stage(self, user_id: str, path_id: str, 
                       stage_index: int) -> Dict[str, Any]:
        """Завершение этапа"""
        if path_id not in self.user_progress.get(user_id, {}):
            return {"error": "Path not started"}
            
        path = self.paths.get(path_id)
        if not path:
            return {"error": "Path not found"}
            
        progress = self.user_progress[user_id][path_id]
        
        if stage_index not in progress["completed_stages"]:
            progress["completed_stages"].append(stage_index)
            
        progress["current_stage"] = stage_index + 1
        
        # Проверка завершения
        if len(progress["completed_stages"]) >= len(path.stages):
            progress["status"] = "completed"
            progress["completed_at"] = datetime.now().isoformat()
            
        return {
            "path_id": path_id,
            "completed_stages": progress["completed_stages"],
            "total_stages": len(path.stages),
            "status": progress["status"],
            "next_stage": path.stages[progress["current_stage"]] 
                         if progress["current_stage"] < len(path.stages) else None
        }


class EnvironmentManager:
    """Менеджер сред"""
    
    def __init__(self):
        self.environments: Dict[str, Environment] = {}
        self.quotas: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "max_environments": 5,
            "max_cpu": 16,
            "max_memory_gb": 64,
            "max_storage_gb": 500
        })
        
    def create_environment(self, env_config: Dict[str, Any]) -> Optional[Environment]:
        """Создание среды"""
        team_id = env_config.get("team_id")
        
        # Проверка квот
        team_envs = [e for e in self.environments.values() if e.team_id == team_id]
        quota = self.quotas[team_id]
        
        if len(team_envs) >= quota["max_environments"]:
            return None
            
        total_cpu = sum(e.cpu_limit for e in team_envs)
        if total_cpu + env_config.get("cpu_limit", 4) > quota["max_cpu"]:
            return None
            
        env = Environment(
            env_id=f"env_{uuid.uuid4().hex[:8]}",
            name=env_config.get("name", "unnamed"),
            env_type=EnvironmentType(env_config.get("type", "development")),
            team_id=team_id,
            cloud_provider=env_config.get("cloud_provider", "aws"),
            region=env_config.get("region", "us-east-1"),
            cpu_limit=env_config.get("cpu_limit", 4),
            memory_limit_gb=env_config.get("memory_limit_gb", 8),
            storage_limit_gb=env_config.get("storage_limit_gb", 100)
        )
        
        # Установка срока действия для не-production сред
        if env.env_type in [EnvironmentType.SANDBOX, EnvironmentType.PREVIEW]:
            env.expires_at = datetime.now() + timedelta(days=7)
        elif env.env_type == EnvironmentType.TESTING:
            env.expires_at = datetime.now() + timedelta(days=30)
            
        # Расчёт стоимости
        env.estimated_daily_cost = self._estimate_daily_cost(env)
        
        self.environments[env.env_id] = env
        return env
        
    def _estimate_daily_cost(self, env: Environment) -> float:
        """Оценка дневной стоимости"""
        # Упрощённая оценка
        cpu_cost = env.cpu_limit * 0.5  # $0.50 per vCPU per day
        memory_cost = env.memory_limit_gb * 0.1  # $0.10 per GB per day
        storage_cost = env.storage_limit_gb * 0.01  # $0.01 per GB per day
        
        return cpu_cost + memory_cost + storage_cost
        
    def delete_environment(self, env_id: str) -> bool:
        """Удаление среды"""
        if env_id in self.environments:
            del self.environments[env_id]
            return True
        return False
        
    def get_team_environments(self, team_id: str) -> List[Environment]:
        """Получение сред команды"""
        return [e for e in self.environments.values() if e.team_id == team_id]
        
    def cleanup_expired_environments(self) -> List[str]:
        """Очистка истёкших сред"""
        now = datetime.now()
        expired = []
        
        for env_id, env in list(self.environments.items()):
            if env.expires_at and env.expires_at < now:
                del self.environments[env_id]
                expired.append(env_id)
                
        return expired
        
    def set_team_quota(self, team_id: str, quotas: Dict[str, Any]):
        """Установка квот команды"""
        self.quotas[team_id].update(quotas)


class ServiceCatalog:
    """Каталог сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        
    def register_service(self, service: Service) -> bool:
        """Регистрация сервиса"""
        if service.service_id in self.services:
            return False
            
        self.services[service.service_id] = service
        self.categories[service.category].append(service.service_id)
        
        return True
        
    def get_service(self, service_id: str) -> Optional[Service]:
        """Получение сервиса"""
        return self.services.get(service_id)
        
    def search_services(self, query: str = "",
                        category: Optional[str] = None,
                        tier: Optional[ServiceTier] = None) -> List[Service]:
        """Поиск сервисов"""
        results = list(self.services.values())
        
        if query:
            query_lower = query.lower()
            results = [s for s in results
                      if query_lower in s.name.lower() or query_lower in s.description.lower()]
                      
        if category:
            results = [s for s in results if s.category == category]
            
        if tier:
            results = [s for s in results if s.tier == tier]
            
        return sorted(results, key=lambda s: s.tier.value)
        
    def get_service_dependencies(self, service_id: str,
                                  include_transitive: bool = True) -> List[str]:
        """Получение зависимостей сервиса"""
        service = self.services.get(service_id)
        if not service:
            return []
            
        deps = set(service.dependencies)
        
        if include_transitive:
            to_process = list(service.dependencies)
            while to_process:
                dep_id = to_process.pop()
                dep_service = self.services.get(dep_id)
                if dep_service:
                    for sub_dep in dep_service.dependencies:
                        if sub_dep not in deps:
                            deps.add(sub_dep)
                            to_process.append(sub_dep)
                            
        return list(deps)
        
    def update_service_status(self, service_id: str, status: str,
                              version: Optional[str] = None) -> bool:
        """Обновление статуса сервиса"""
        service = self.services.get(service_id)
        if not service:
            return False
            
        service.status = status
        service.last_deployment = datetime.now()
        
        if version:
            service.version = version
            
        return True
        
    def get_critical_services(self) -> List[Service]:
        """Получение критичных сервисов"""
        return [s for s in self.services.values() 
                if s.tier == ServiceTier.TIER1_CRITICAL]


class SelfServicePortal:
    """Портал самообслуживания"""
    
    def __init__(self, template_catalog: TemplateCatalog,
                 environment_manager: EnvironmentManager,
                 service_catalog: ServiceCatalog):
        self.template_catalog = template_catalog
        self.environment_manager = environment_manager
        self.service_catalog = service_catalog
        
        self.teams: Dict[str, Team] = {}
        self.requests: Dict[str, ServiceRequest] = {}
        self.approval_workflows: Dict[str, List[str]] = {}  # request_type -> approvers
        
    def register_team(self, team: Team) -> bool:
        """Регистрация команды"""
        if team.team_id in self.teams:
            return False
            
        self.teams[team.team_id] = team
        return True
        
    def configure_approval_workflow(self, request_type: str, approvers: List[str]):
        """Настройка workflow согласования"""
        self.approval_workflows[request_type] = approvers
        
    def submit_request(self, request: ServiceRequest) -> str:
        """Подача запроса"""
        # Установка approvers из workflow
        if request.request_type in self.approval_workflows:
            request.approvers = self.approval_workflows[request.request_type]
        else:
            request.approvers = []
            
        # Если нет approvers - автоматическое одобрение
        if not request.approvers:
            request.status = RequestStatus.APPROVED
            
        self.requests[request.request_id] = request
        
        return request.request_id
        
    def approve_request(self, request_id: str, approver: str) -> bool:
        """Одобрение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        if approver not in request.approvers:
            return False
            
        if approver in request.approved_by:
            return False
            
        request.approved_by.append(approver)
        request.updated_at = datetime.now()
        
        # Проверка полного одобрения
        if len(request.approved_by) >= len(request.approvers):
            request.status = RequestStatus.APPROVED
            
        return True
        
    def reject_request(self, request_id: str, rejector: str, reason: str) -> bool:
        """Отклонение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        request.status = RequestStatus.REJECTED
        request.rejected_by = rejector
        request.rejection_reason = reason
        request.updated_at = datetime.now()
        
        return True
        
    async def execute_request(self, request_id: str) -> Dict[str, Any]:
        """Выполнение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return {"error": "Request not found"}
            
        if request.status != RequestStatus.APPROVED:
            return {"error": "Request not approved"}
            
        request.status = RequestStatus.IN_PROGRESS
        request.updated_at = datetime.now()
        
        try:
            result = await self._process_request(request)
            
            request.status = RequestStatus.COMPLETED
            request.result = result
            request.completed_at = datetime.now()
            
            return result
            
        except Exception as e:
            request.status = RequestStatus.FAILED
            request.error = str(e)
            return {"error": str(e)}
            
    async def _process_request(self, request: ServiceRequest) -> Dict[str, Any]:
        """Обработка запроса"""
        if request.request_type == "create_project":
            return await self._create_project(request)
        elif request.request_type == "provision_environment":
            return await self._provision_environment(request)
        elif request.request_type == "register_service":
            return await self._register_service(request)
        else:
            return {"error": f"Unknown request type: {request.request_type}"}
            
    async def _create_project(self, request: ServiceRequest) -> Dict[str, Any]:
        """Создание проекта"""
        template_id = request.parameters.get("template_id")
        project_params = request.parameters.get("project_params", {})
        
        result = self.template_catalog.instantiate_template(template_id, project_params)
        
        await asyncio.sleep(0.5)  # Симуляция создания
        
        return result
        
    async def _provision_environment(self, request: ServiceRequest) -> Dict[str, Any]:
        """Провижнинг среды"""
        env_config = request.parameters
        env_config["team_id"] = request.team_id
        
        env = self.environment_manager.create_environment(env_config)
        
        if not env:
            return {"error": "Failed to create environment - quota exceeded"}
            
        await asyncio.sleep(0.5)  # Симуляция провижнинга
        
        return {
            "environment_id": env.env_id,
            "name": env.name,
            "type": env.env_type.value,
            "estimated_daily_cost": env.estimated_daily_cost,
            "expires_at": env.expires_at.isoformat() if env.expires_at else None
        }
        
    async def _register_service(self, request: ServiceRequest) -> Dict[str, Any]:
        """Регистрация сервиса"""
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=request.parameters.get("name"),
            description=request.parameters.get("description", ""),
            team_id=request.team_id,
            tier=ServiceTier(request.parameters.get("tier", "tier3_standard")),
            repository_url=request.parameters.get("repository_url", "")
        )
        
        self.service_catalog.register_service(service)
        
        return {
            "service_id": service.service_id,
            "name": service.name,
            "tier": service.tier.value
        }
        
    def get_team_requests(self, team_id: str,
                          status: Optional[RequestStatus] = None) -> List[ServiceRequest]:
        """Получение запросов команды"""
        results = [r for r in self.requests.values() if r.team_id == team_id]
        
        if status:
            results = [r for r in results if r.status == status]
            
        return sorted(results, key=lambda r: r.created_at, reverse=True)


class CostManager:
    """Менеджер затрат"""
    
    def __init__(self, environment_manager: EnvironmentManager):
        self.environment_manager = environment_manager
        self.cost_records: List[CostRecord] = []
        self.budgets: Dict[str, float] = {}  # team_id -> monthly_budget
        self.alerts: List[Dict[str, Any]] = []
        
    def record_cost(self, record: CostRecord):
        """Запись затрат"""
        self.cost_records.append(record)
        
        # Проверка бюджета
        self._check_budget_alerts(record.team_id)
        
    def set_budget(self, team_id: str, monthly_budget: float):
        """Установка бюджета"""
        self.budgets[team_id] = monthly_budget
        
    def _check_budget_alerts(self, team_id: str):
        """Проверка алертов бюджета"""
        if team_id not in self.budgets:
            return
            
        budget = self.budgets[team_id]
        current_spend = self.get_team_monthly_spend(team_id)
        
        usage_percent = (current_spend / budget) * 100
        
        if usage_percent >= 100:
            self._create_alert(team_id, "budget_exceeded", 
                             f"Budget exceeded: ${current_spend:.2f} / ${budget:.2f}")
        elif usage_percent >= 80:
            self._create_alert(team_id, "budget_warning",
                             f"80% budget used: ${current_spend:.2f} / ${budget:.2f}")
                             
    def _create_alert(self, team_id: str, alert_type: str, message: str):
        """Создание алерта"""
        self.alerts.append({
            "team_id": team_id,
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_team_monthly_spend(self, team_id: str) -> float:
        """Получение месячных затрат команды"""
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        
        return sum(
            r.amount for r in self.cost_records
            if r.team_id == team_id and r.period_start >= start_of_month
        )
        
    def get_cost_breakdown(self, team_id: str, 
                           period_days: int = 30) -> Dict[str, Any]:
        """Получение разбивки затрат"""
        cutoff = datetime.now() - timedelta(days=period_days)
        
        records = [r for r in self.cost_records
                   if r.team_id == team_id and r.period_start >= cutoff]
                   
        by_category = defaultdict(float)
        by_service = defaultdict(float)
        by_environment = defaultdict(float)
        
        for record in records:
            by_category[record.category.value] += record.amount
            by_service[record.service_id] += record.amount
            by_environment[record.environment_id] += record.amount
            
        return {
            "team_id": team_id,
            "period_days": period_days,
            "total": sum(r.amount for r in records),
            "by_category": dict(by_category),
            "by_service": dict(by_service),
            "by_environment": dict(by_environment),
            "record_count": len(records)
        }
        
    def get_cost_forecast(self, team_id: str) -> Dict[str, Any]:
        """Прогноз затрат"""
        # Получение среднедневных затрат за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)
        
        records = [r for r in self.cost_records
                   if r.team_id == team_id and r.period_start >= week_ago]
                   
        if not records:
            return {"error": "Insufficient data"}
            
        total_week = sum(r.amount for r in records)
        daily_avg = total_week / 7
        
        # Прогноз на конец месяца
        today = datetime.now()
        days_remaining = (today.replace(month=today.month % 12 + 1, day=1) 
                         - timedelta(days=1)).day - today.day
                         
        forecasted_spend = self.get_team_monthly_spend(team_id) + (daily_avg * days_remaining)
        
        budget = self.budgets.get(team_id, 0)
        
        return {
            "team_id": team_id,
            "current_month_spend": self.get_team_monthly_spend(team_id),
            "daily_average": daily_avg,
            "days_remaining": days_remaining,
            "forecasted_month_end": forecasted_spend,
            "budget": budget,
            "forecasted_variance": forecasted_spend - budget if budget > 0 else None
        }
        
    def get_cost_optimization_recommendations(self, team_id: str) -> List[Dict[str, Any]]:
        """Рекомендации по оптимизации затрат"""
        recommendations = []
        
        # Проверка неиспользуемых сред
        team_envs = self.environment_manager.get_team_environments(team_id)
        for env in team_envs:
            if env.env_type in [EnvironmentType.SANDBOX, EnvironmentType.PREVIEW]:
                recommendations.append({
                    "type": "cleanup",
                    "resource": f"Environment: {env.name}",
                    "reason": f"Temporary environment ({env.env_type.value}) still active",
                    "potential_savings": env.estimated_daily_cost * 30
                })
                
        # Проверка oversized сред
        for env in team_envs:
            if env.cpu_limit > 8 and env.env_type == EnvironmentType.DEVELOPMENT:
                recommendations.append({
                    "type": "resize",
                    "resource": f"Environment: {env.name}",
                    "reason": "Development environment may be oversized",
                    "potential_savings": (env.cpu_limit - 4) * 0.5 * 30
                })
                
        return recommendations


class PlatformAnalytics:
    """Аналитика платформы"""
    
    def __init__(self, portal: SelfServicePortal,
                 cost_manager: CostManager):
        self.portal = portal
        self.cost_manager = cost_manager
        self.events: List[Dict[str, Any]] = []
        
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Запись события"""
        self.events.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ограничение истории
        if len(self.events) > 10000:
            self.events = self.events[-5000:]
            
    def get_platform_metrics(self) -> Dict[str, Any]:
        """Получение метрик платформы"""
        return {
            "teams": {
                "total": len(self.portal.teams),
                "active": len([t for t in self.portal.teams.values()
                              if t.created_at > datetime.now() - timedelta(days=30)])
            },
            "environments": {
                "total": len(self.portal.environment_manager.environments),
                "by_type": self._count_environments_by_type()
            },
            "services": {
                "total": len(self.portal.service_catalog.services),
                "by_tier": self._count_services_by_tier()
            },
            "templates": {
                "total": len(self.portal.template_catalog.templates),
                "total_usage": sum(t.usage_count 
                                  for t in self.portal.template_catalog.templates.values())
            },
            "requests": {
                "total": len(self.portal.requests),
                "by_status": self._count_requests_by_status()
            }
        }
        
    def _count_environments_by_type(self) -> Dict[str, int]:
        """Подсчёт сред по типу"""
        counts = defaultdict(int)
        for env in self.portal.environment_manager.environments.values():
            counts[env.env_type.value] += 1
        return dict(counts)
        
    def _count_services_by_tier(self) -> Dict[str, int]:
        """Подсчёт сервисов по уровню"""
        counts = defaultdict(int)
        for service in self.portal.service_catalog.services.values():
            counts[service.tier.value] += 1
        return dict(counts)
        
    def _count_requests_by_status(self) -> Dict[str, int]:
        """Подсчёт запросов по статусу"""
        counts = defaultdict(int)
        for request in self.portal.requests.values():
            counts[request.status.value] += 1
        return dict(counts)
        
    def get_adoption_metrics(self) -> Dict[str, Any]:
        """Метрики адаптации"""
        now = datetime.now()
        
        # Активные пользователи (сделавшие запрос за последние 30 дней)
        active_requesters = set()
        for request in self.portal.requests.values():
            if request.created_at > now - timedelta(days=30):
                active_requesters.add(request.requester_email)
                
        # Популярные шаблоны
        popular_templates = self.portal.template_catalog.get_popular_templates(5)
        
        return {
            "active_users_30d": len(active_requesters),
            "new_environments_30d": len([
                e for e in self.portal.environment_manager.environments.values()
                if e.created_at > now - timedelta(days=30)
            ]),
            "requests_30d": len([
                r for r in self.portal.requests.values()
                if r.created_at > now - timedelta(days=30)
            ]),
            "popular_templates": [
                {"name": t.name, "usage": t.usage_count}
                for t in popular_templates
            ],
            "avg_request_completion_time_hours": self._calculate_avg_completion_time()
        }
        
    def _calculate_avg_completion_time(self) -> float:
        """Расчёт среднего времени выполнения запроса"""
        completed = [
            r for r in self.portal.requests.values()
            if r.status == RequestStatus.COMPLETED and r.completed_at
        ]
        
        if not completed:
            return 0
            
        total_hours = sum(
            (r.completed_at - r.created_at).total_seconds() / 3600
            for r in completed
        )
        
        return total_hours / len(completed)


class PlatformEngineeringSystem:
    """Система платформенной инженерии"""
    
    def __init__(self):
        self.template_catalog = TemplateCatalog()
        self.environment_manager = EnvironmentManager()
        self.service_catalog = ServiceCatalog()
        self.portal = SelfServicePortal(
            self.template_catalog,
            self.environment_manager,
            self.service_catalog
        )
        self.golden_path_manager = GoldenPathManager(self.template_catalog)
        self.cost_manager = CostManager(self.environment_manager)
        self.analytics = PlatformAnalytics(self.portal, self.cost_manager)
        
    def initialize(self):
        """Инициализация системы"""
        # Создание стандартных шаблонов
        self._create_default_templates()
        
        # Создание золотых путей
        self._create_default_golden_paths()
        
        # Настройка workflows
        self.portal.configure_approval_workflow("provision_environment", [])
        self.portal.configure_approval_workflow("register_service", ["platform-team@company.com"])
        
    def _create_default_templates(self):
        """Создание шаблонов по умолчанию"""
        templates = [
            Template(
                template_id="microservice-python",
                name="Python Microservice",
                description="Production-ready Python microservice with FastAPI",
                template_type=TemplateType.MICROSERVICE,
                version="1.0.0",
                repository_url="https://github.com/company/template-python-microservice",
                parameters={"service_name": "string", "port": "number"},
                defaults={"port": 8080},
                required_params=["service_name"],
                tags=["python", "fastapi", "microservice"]
            ),
            Template(
                template_id="microservice-go",
                name="Go Microservice",
                description="High-performance Go microservice template",
                template_type=TemplateType.MICROSERVICE,
                version="1.0.0",
                repository_url="https://github.com/company/template-go-microservice",
                parameters={"service_name": "string", "port": "number"},
                defaults={"port": 8080},
                required_params=["service_name"],
                tags=["go", "microservice", "grpc"]
            ),
            Template(
                template_id="frontend-react",
                name="React Frontend",
                description="Modern React frontend with TypeScript",
                template_type=TemplateType.FRONTEND,
                version="1.0.0",
                repository_url="https://github.com/company/template-react-frontend",
                parameters={"app_name": "string", "api_url": "string"},
                required_params=["app_name"],
                tags=["react", "typescript", "frontend"]
            ),
            Template(
                template_id="data-pipeline-spark",
                name="Spark Data Pipeline",
                description="Apache Spark data pipeline template",
                template_type=TemplateType.DATA_PIPELINE,
                version="1.0.0",
                repository_url="https://github.com/company/template-spark-pipeline",
                parameters={"pipeline_name": "string", "input_format": "string"},
                required_params=["pipeline_name"],
                tags=["spark", "data", "etl"]
            )
        ]
        
        for template in templates:
            self.template_catalog.register_template(template)
            
    def _create_default_golden_paths(self):
        """Создание золотых путей по умолчанию"""
        paths = [
            GoldenPath(
                path_id="new-microservice",
                name="New Microservice",
                description="Create and deploy a new microservice",
                stages=[
                    {"name": "Choose Template", "description": "Select appropriate template"},
                    {"name": "Configure", "description": "Set up service configuration"},
                    {"name": "Create Repository", "description": "Initialize git repository"},
                    {"name": "Setup CI/CD", "description": "Configure pipelines"},
                    {"name": "Deploy to Dev", "description": "First deployment"},
                    {"name": "Register Service", "description": "Add to service catalog"}
                ],
                recommended_templates=["microservice-python", "microservice-go"],
                required_tools=["git", "docker", "kubectl"],
                target_audience=["backend", "platform"],
                estimated_setup_time_hours=2.0
            ),
            GoldenPath(
                path_id="new-frontend",
                name="New Frontend Application",
                description="Create and deploy a new frontend application",
                stages=[
                    {"name": "Choose Template", "description": "Select frontend template"},
                    {"name": "Configure", "description": "Set up application configuration"},
                    {"name": "Create Repository", "description": "Initialize git repository"},
                    {"name": "Setup CI/CD", "description": "Configure build pipelines"},
                    {"name": "Deploy Preview", "description": "Create preview environment"},
                    {"name": "Go Live", "description": "Production deployment"}
                ],
                recommended_templates=["frontend-react"],
                required_tools=["git", "npm", "node"],
                target_audience=["frontend"],
                estimated_setup_time_hours=1.5
            )
        ]
        
        for path in paths:
            self.golden_path_manager.create_golden_path(path)
            
    def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        metrics = self.analytics.get_platform_metrics()
        adoption = self.analytics.get_adoption_metrics()
        
        return {
            "platform": "Platform Engineering System v1.0",
            "metrics": metrics,
            "adoption": adoption,
            "health": "healthy"
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 35: Platform Engineering Automation")
    print("=" * 60)
    
    # Создание системы
    platform = PlatformEngineeringSystem()
    platform.initialize()
    
    # Регистрация команды
    team = Team(
        team_id="team_backend",
        name="Backend Team",
        description="Core backend services team",
        owner_email="backend-lead@company.com",
        members=["dev1@company.com", "dev2@company.com"],
        budget_monthly=5000.0
    )
    platform.portal.register_team(team)
    print(f"✓ Team registered: {team.name}")
    
    # Установка бюджета
    platform.cost_manager.set_budget(team.team_id, team.budget_monthly)
    
    # Поиск шаблонов
    templates = platform.template_catalog.search_templates(
        template_type=TemplateType.MICROSERVICE
    )
    print(f"✓ Found {len(templates)} microservice templates")
    
    # Получение рекомендованного golden path
    path = platform.golden_path_manager.get_recommended_path(
        use_case="backend",
        team_size=3,
        tech_stack=["python", "docker", "kubernetes"]
    )
    if path:
        print(f"✓ Recommended path: {path.name}")
        
    # Создание запроса на среду
    request = ServiceRequest(
        request_id=f"req_{uuid.uuid4().hex[:8]}",
        request_type="provision_environment",
        requester_email="dev1@company.com",
        team_id=team.team_id,
        parameters={
            "name": "dev-backend-1",
            "type": "development",
            "cpu_limit": 4,
            "memory_limit_gb": 8
        }
    )
    
    request_id = platform.portal.submit_request(request)
    print(f"✓ Request submitted: {request_id}")
    
    # Выполнение запроса (автоматически одобрен)
    async def execute():
        result = await platform.portal.execute_request(request_id)
        return result
        
    result = asyncio.run(execute())
    if "environment_id" in result:
        print(f"✓ Environment created: {result['environment_id']}")
        print(f"   Estimated daily cost: ${result['estimated_daily_cost']:.2f}")
        
    # Получение статуса
    status = platform.get_system_status()
    print(f"\n📊 Platform Status:")
    print(f"   Total Teams: {status['metrics']['teams']['total']}")
    print(f"   Total Templates: {status['metrics']['templates']['total']}")
    print(f"   Total Environments: {status['metrics']['environments']['total']}")
    print(f"   Total Services: {status['metrics']['services']['total']}")
    
    # Рекомендации по оптимизации
    recommendations = platform.cost_manager.get_cost_optimization_recommendations(team.team_id)
    print(f"\n💡 Cost Optimization Recommendations: {len(recommendations)}")
    
    print("\n" + "=" * 60)
    print("Platform Engineering System initialized successfully!")
    print("=" * 60)
