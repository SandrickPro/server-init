#!/usr/bin/env python3
"""
Server Init - Iteration 39: Platform Engineering & Developer Experience
Платформенная инженерия и опыт разработчика

Функционал:
- Internal Developer Platform - внутренняя платформа разработчика
- Self-Service Portal - портал самообслуживания
- Service Catalog - каталог сервисов
- Golden Paths - золотые пути
- Developer Onboarding - онбординг разработчиков
- Documentation as Code - документация как код
- Developer Metrics - метрики разработчиков
- Platform APIs - API платформы
"""

import json
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import re


class ServiceType(Enum):
    """Тип сервиса"""
    MICROSERVICE = "microservice"
    API = "api"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    QUEUE = "queue"
    CACHE = "cache"
    ML_MODEL = "ml_model"
    SERVERLESS = "serverless"


class EnvironmentType(Enum):
    """Тип окружения"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class TemplateCategory(Enum):
    """Категория шаблона"""
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    PIPELINE = "pipeline"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"


class RequestStatus(Enum):
    """Статус запроса"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OnboardingStage(Enum):
    """Этап онбординга"""
    WELCOME = "welcome"
    ACCOUNT_SETUP = "account_setup"
    TOOL_ACCESS = "tool_access"
    TRAINING = "training"
    FIRST_PROJECT = "first_project"
    COMPLETED = "completed"


@dataclass
class ServiceTemplate:
    """Шаблон сервиса"""
    template_id: str
    name: str
    description: str
    category: TemplateCategory
    service_type: ServiceType
    
    # Технологии
    language: str = ""
    framework: str = ""
    
    # Репозиторий
    repo_template: str = ""
    
    # Конфигурация
    default_config: Dict[str, Any] = field(default_factory=dict)
    required_inputs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Компоненты
    includes_ci_cd: bool = True
    includes_monitoring: bool = True
    includes_docs: bool = True
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    owner: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Service:
    """Сервис в каталоге"""
    service_id: str
    name: str
    description: str
    service_type: ServiceType
    
    # Владение
    team: str = ""
    owner: str = ""
    
    # Репозитории
    repositories: List[str] = field(default_factory=list)
    
    # Конфигурация
    tier: str = "standard"  # standard, premium, critical
    sla: str = "99.9%"
    
    # Зависимости
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    # Окружения
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Документация
    docs_url: str = ""
    api_spec_url: str = ""
    runbook_url: str = ""
    
    # Статус
    status: str = "active"
    health_status: str = "healthy"
    
    # Метрики
    deployment_frequency: float = 0.0
    lead_time_hours: float = 0.0
    mttr_hours: float = 0.0
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelfServiceRequest:
    """Запрос самообслуживания"""
    request_id: str
    request_type: str
    title: str
    description: str
    
    # Запрашивающий
    requester: str
    team: str
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Статус
    status: RequestStatus = RequestStatus.PENDING
    
    # Одобрение
    requires_approval: bool = False
    approvers: List[str] = field(default_factory=list)
    approved_by: Optional[str] = None
    
    # Выполнение
    workflow_id: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class GoldenPath:
    """Золотой путь"""
    path_id: str
    name: str
    description: str
    
    # Тип
    use_case: str = ""
    target_audience: str = ""
    
    # Шаги
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Ресурсы
    templates: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    documentation: List[str] = field(default_factory=list)
    
    # Результаты
    expected_outcome: str = ""
    estimated_time: str = ""
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Developer:
    """Разработчик"""
    developer_id: str
    name: str
    email: str
    
    # Организация
    team: str = ""
    role: str = "developer"
    
    # Онбординг
    onboarding_stage: OnboardingStage = OnboardingStage.WELCOME
    onboarding_progress: float = 0.0
    onboarding_started_at: Optional[datetime] = None
    onboarding_completed_at: Optional[datetime] = None
    
    # Доступы
    tool_access: List[str] = field(default_factory=list)
    service_access: List[str] = field(default_factory=list)
    
    # Активность
    last_activity: Optional[datetime] = None
    deployments_count: int = 0
    prs_merged: int = 0
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Documentation:
    """Документация"""
    doc_id: str
    title: str
    content: str
    
    # Тип
    doc_type: str = "guide"  # guide, tutorial, reference, runbook
    
    # Связи
    service_id: Optional[str] = None
    team: Optional[str] = None
    
    # Версионирование
    version: str = "1.0"
    source_repo: str = ""
    source_path: str = ""
    
    # Статус
    status: str = "published"  # draft, review, published, archived
    last_reviewed: Optional[datetime] = None
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DeveloperMetrics:
    """Метрики разработчика"""
    developer_id: str
    period_start: datetime
    period_end: datetime
    
    # Активность
    commits_count: int = 0
    prs_opened: int = 0
    prs_merged: int = 0
    prs_reviewed: int = 0
    
    # Качество
    code_coverage_avg: float = 0.0
    bugs_introduced: int = 0
    bugs_fixed: int = 0
    
    # Velocity
    story_points_completed: int = 0
    tasks_completed: int = 0
    avg_pr_cycle_time_hours: float = 0.0
    
    # Collaboration
    comments_given: int = 0
    comments_received: int = 0
    pair_programming_hours: float = 0.0


class ServiceCatalog:
    """Каталог сервисов"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.templates: Dict[str, ServiceTemplate] = {}
        
    def register_service(self, service: Service) -> str:
        """Регистрация сервиса"""
        self.services[service.service_id] = service
        return service.service_id
        
    def register_template(self, template: ServiceTemplate) -> str:
        """Регистрация шаблона"""
        self.templates[template.template_id] = template
        return template.template_id
        
    def get_service(self, service_id: str) -> Optional[Service]:
        """Получение сервиса"""
        return self.services.get(service_id)
        
    def search_services(self, 
                        query: Optional[str] = None,
                        service_type: Optional[ServiceType] = None,
                        team: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> List[Service]:
        """Поиск сервисов"""
        results = list(self.services.values())
        
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.name.lower() or query_lower in s.description.lower()
            ]
            
        if service_type:
            results = [s for s in results if s.service_type == service_type]
            
        if team:
            results = [s for s in results if s.team == team]
            
        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]
            
        return results
        
    def get_service_dependencies(self, service_id: str) -> Dict[str, Any]:
        """Получение зависимостей сервиса"""
        service = self.services.get(service_id)
        if not service:
            return {}
            
        return {
            "service_id": service_id,
            "dependencies": [
                {
                    "id": dep_id,
                    "name": self.services[dep_id].name if dep_id in self.services else dep_id,
                    "type": self.services[dep_id].service_type.value if dep_id in self.services else "unknown"
                }
                for dep_id in service.dependencies
            ],
            "dependents": [
                {
                    "id": dep_id,
                    "name": self.services[dep_id].name if dep_id in self.services else dep_id,
                    "type": self.services[dep_id].service_type.value if dep_id in self.services else "unknown"
                }
                for dep_id in service.dependents
            ]
        }
        
    def get_templates_by_type(self, service_type: ServiceType) -> List[ServiceTemplate]:
        """Получение шаблонов по типу"""
        return [t for t in self.templates.values() if t.service_type == service_type]
        
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Статистика каталога"""
        by_type = defaultdict(int)
        by_team = defaultdict(int)
        by_tier = defaultdict(int)
        
        for service in self.services.values():
            by_type[service.service_type.value] += 1
            by_team[service.team] += 1
            by_tier[service.tier] += 1
            
        return {
            "total_services": len(self.services),
            "total_templates": len(self.templates),
            "by_type": dict(by_type),
            "by_team": dict(by_team),
            "by_tier": dict(by_tier),
            "healthy_services": len([s for s in self.services.values() if s.health_status == "healthy"]),
            "unhealthy_services": len([s for s in self.services.values() if s.health_status != "healthy"])
        }


class SelfServicePortal:
    """Портал самообслуживания"""
    
    def __init__(self, catalog: ServiceCatalog):
        self.catalog = catalog
        self.requests: Dict[str, SelfServiceRequest] = {}
        self.workflows: Dict[str, Callable] = {}
        self.approval_rules: List[Dict[str, Any]] = []
        
    def register_workflow(self, request_type: str, workflow: Callable):
        """Регистрация workflow"""
        self.workflows[request_type] = workflow
        
    def add_approval_rule(self, rule: Dict[str, Any]):
        """Добавление правила одобрения"""
        self.approval_rules.append(rule)
        
    async def create_request(self, request: SelfServiceRequest) -> str:
        """Создание запроса"""
        # Проверка необходимости одобрения
        request.requires_approval = self._check_requires_approval(request)
        
        if request.requires_approval:
            request.approvers = self._get_approvers(request)
            request.status = RequestStatus.PENDING
        else:
            request.status = RequestStatus.APPROVED
            
        self.requests[request.request_id] = request
        
        # Автоматическое выполнение если не требуется одобрение
        if not request.requires_approval:
            await self.execute_request(request.request_id)
            
        return request.request_id
        
    def _check_requires_approval(self, request: SelfServiceRequest) -> bool:
        """Проверка необходимости одобрения"""
        for rule in self.approval_rules:
            if rule.get("request_type") == request.request_type:
                # Проверка условий
                if "environment" in rule:
                    if request.parameters.get("environment") in rule["environment"]:
                        return True
                        
                if "tier" in rule:
                    if request.parameters.get("tier") in rule["tier"]:
                        return True
                        
                if "always" in rule and rule["always"]:
                    return True
                    
        return False
        
    def _get_approvers(self, request: SelfServiceRequest) -> List[str]:
        """Получение списка approvers"""
        approvers = set()
        
        for rule in self.approval_rules:
            if rule.get("request_type") == request.request_type:
                if "approvers" in rule:
                    approvers.update(rule["approvers"])
                    
        return list(approvers) or ["platform-team"]
        
    def approve_request(self, request_id: str, approver: str) -> bool:
        """Одобрение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        if approver not in request.approvers:
            return False
            
        request.approved_by = approver
        request.status = RequestStatus.APPROVED
        
        return True
        
    def reject_request(self, request_id: str, approver: str, reason: str) -> bool:
        """Отклонение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return False
            
        request.status = RequestStatus.REJECTED
        request.error = reason
        
        return True
        
    async def execute_request(self, request_id: str) -> Dict[str, Any]:
        """Выполнение запроса"""
        request = self.requests.get(request_id)
        if not request:
            return {"error": "Request not found"}
            
        if request.status != RequestStatus.APPROVED:
            return {"error": "Request not approved"}
            
        workflow = self.workflows.get(request.request_type)
        if not workflow:
            return {"error": f"No workflow for request type: {request.request_type}"}
            
        request.status = RequestStatus.IN_PROGRESS
        
        try:
            if asyncio.iscoroutinefunction(workflow):
                result = await workflow(request)
            else:
                result = workflow(request)
                
            request.output = result
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.now()
            
            return result
            
        except Exception as e:
            request.status = RequestStatus.FAILED
            request.error = str(e)
            return {"error": str(e)}
            
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса запроса"""
        request = self.requests.get(request_id)
        if not request:
            return None
            
        return {
            "request_id": request.request_id,
            "type": request.request_type,
            "status": request.status.value,
            "requires_approval": request.requires_approval,
            "approved_by": request.approved_by,
            "output": request.output,
            "error": request.error,
            "created_at": request.created_at.isoformat(),
            "completed_at": request.completed_at.isoformat() if request.completed_at else None
        }
        
    def get_pending_requests(self, approver: Optional[str] = None) -> List[SelfServiceRequest]:
        """Получение ожидающих запросов"""
        pending = [r for r in self.requests.values() if r.status == RequestStatus.PENDING]
        
        if approver:
            pending = [r for r in pending if approver in r.approvers]
            
        return pending


class GoldenPathManager:
    """Менеджер золотых путей"""
    
    def __init__(self, catalog: ServiceCatalog):
        self.catalog = catalog
        self.paths: Dict[str, GoldenPath] = {}
        
    def create_path(self, path: GoldenPath) -> str:
        """Создание золотого пути"""
        self.paths[path.path_id] = path
        return path.path_id
        
    def get_path(self, path_id: str) -> Optional[GoldenPath]:
        """Получение пути"""
        return self.paths.get(path_id)
        
    def find_path_for_use_case(self, use_case: str) -> List[GoldenPath]:
        """Поиск пути по use case"""
        use_case_lower = use_case.lower()
        return [
            p for p in self.paths.values()
            if use_case_lower in p.use_case.lower() or use_case_lower in p.name.lower()
        ]
        
    def get_recommended_paths(self, 
                               team: Optional[str] = None,
                               experience_level: str = "intermediate") -> List[GoldenPath]:
        """Получение рекомендованных путей"""
        paths = list(self.paths.values())
        
        # Фильтрация по уровню опыта
        if experience_level == "beginner":
            paths = [p for p in paths if "beginner" in p.target_audience.lower() or "all" in p.target_audience.lower()]
        elif experience_level == "advanced":
            paths = [p for p in paths if "advanced" in p.target_audience.lower() or "all" in p.target_audience.lower()]
            
        return paths[:5]  # Top 5
        
    def validate_path_completion(self, path_id: str, 
                                  completed_steps: List[str]) -> Dict[str, Any]:
        """Валидация завершения пути"""
        path = self.paths.get(path_id)
        if not path:
            return {"error": "Path not found"}
            
        total_steps = len(path.steps)
        completed_count = len([s for s in path.steps if s.get("id") in completed_steps])
        
        return {
            "path_id": path_id,
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "progress_percent": (completed_count / total_steps * 100) if total_steps > 0 else 0,
            "is_complete": completed_count == total_steps,
            "remaining_steps": [s for s in path.steps if s.get("id") not in completed_steps]
        }


class DeveloperOnboarding:
    """Онбординг разработчиков"""
    
    def __init__(self):
        self.developers: Dict[str, Developer] = {}
        self.onboarding_tasks: Dict[str, List[Dict[str, Any]]] = {}
        self.tools_access_workflow: Dict[str, Callable] = {}
        
    def start_onboarding(self, developer: Developer) -> str:
        """Начало онбординга"""
        developer.onboarding_started_at = datetime.now()
        developer.onboarding_stage = OnboardingStage.WELCOME
        self.developers[developer.developer_id] = developer
        
        # Создание задач онбординга
        self._create_onboarding_tasks(developer)
        
        return developer.developer_id
        
    def _create_onboarding_tasks(self, developer: Developer):
        """Создание задач онбординга"""
        self.onboarding_tasks[developer.developer_id] = [
            {
                "id": "welcome_1",
                "stage": OnboardingStage.WELCOME,
                "title": "Welcome to the team!",
                "description": "Read the welcome guide and meet your team",
                "completed": False
            },
            {
                "id": "account_1",
                "stage": OnboardingStage.ACCOUNT_SETUP,
                "title": "Set up accounts",
                "description": "Configure your GitHub, Slack, and email accounts",
                "completed": False
            },
            {
                "id": "account_2",
                "stage": OnboardingStage.ACCOUNT_SETUP,
                "title": "Set up local development environment",
                "description": "Install required tools and configure your machine",
                "completed": False
            },
            {
                "id": "tools_1",
                "stage": OnboardingStage.TOOL_ACCESS,
                "title": "Request tool access",
                "description": "Get access to required tools and services",
                "completed": False
            },
            {
                "id": "training_1",
                "stage": OnboardingStage.TRAINING,
                "title": "Complete required training",
                "description": "Complete security and platform training modules",
                "completed": False
            },
            {
                "id": "project_1",
                "stage": OnboardingStage.FIRST_PROJECT,
                "title": "Complete first task",
                "description": "Pick a starter task and submit your first PR",
                "completed": False
            }
        ]
        
    def complete_task(self, developer_id: str, task_id: str) -> Dict[str, Any]:
        """Завершение задачи"""
        if developer_id not in self.developers:
            return {"error": "Developer not found"}
            
        tasks = self.onboarding_tasks.get(developer_id, [])
        
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                break
                
        # Обновление прогресса
        self._update_progress(developer_id)
        
        return self.get_onboarding_status(developer_id)
        
    def _update_progress(self, developer_id: str):
        """Обновление прогресса"""
        developer = self.developers.get(developer_id)
        if not developer:
            return
            
        tasks = self.onboarding_tasks.get(developer_id, [])
        if not tasks:
            return
            
        completed = [t for t in tasks if t["completed"]]
        developer.onboarding_progress = len(completed) / len(tasks) * 100
        
        # Обновление stage
        if all(t["completed"] for t in tasks if t["stage"] == OnboardingStage.WELCOME):
            developer.onboarding_stage = OnboardingStage.ACCOUNT_SETUP
            
        if all(t["completed"] for t in tasks if t["stage"] == OnboardingStage.ACCOUNT_SETUP):
            developer.onboarding_stage = OnboardingStage.TOOL_ACCESS
            
        if all(t["completed"] for t in tasks if t["stage"] == OnboardingStage.TOOL_ACCESS):
            developer.onboarding_stage = OnboardingStage.TRAINING
            
        if all(t["completed"] for t in tasks if t["stage"] == OnboardingStage.TRAINING):
            developer.onboarding_stage = OnboardingStage.FIRST_PROJECT
            
        if all(t["completed"] for t in tasks):
            developer.onboarding_stage = OnboardingStage.COMPLETED
            developer.onboarding_completed_at = datetime.now()
            
    def get_onboarding_status(self, developer_id: str) -> Dict[str, Any]:
        """Получение статуса онбординга"""
        developer = self.developers.get(developer_id)
        if not developer:
            return {"error": "Developer not found"}
            
        tasks = self.onboarding_tasks.get(developer_id, [])
        
        return {
            "developer_id": developer_id,
            "name": developer.name,
            "stage": developer.onboarding_stage.value,
            "progress": developer.onboarding_progress,
            "started_at": developer.onboarding_started_at.isoformat() if developer.onboarding_started_at else None,
            "completed_at": developer.onboarding_completed_at.isoformat() if developer.onboarding_completed_at else None,
            "tasks": {
                "total": len(tasks),
                "completed": len([t for t in tasks if t["completed"]]),
                "pending": [t for t in tasks if not t["completed"]]
            }
        }
        
    def grant_tool_access(self, developer_id: str, tool: str) -> bool:
        """Предоставление доступа к инструменту"""
        developer = self.developers.get(developer_id)
        if not developer:
            return False
            
        if tool not in developer.tool_access:
            developer.tool_access.append(tool)
            
        return True


class DocumentationHub:
    """Центр документации"""
    
    def __init__(self):
        self.documents: Dict[str, Documentation] = {}
        self.doc_index: Dict[str, List[str]] = defaultdict(list)  # tag/type -> doc_ids
        
    def add_document(self, doc: Documentation) -> str:
        """Добавление документа"""
        self.documents[doc.doc_id] = doc
        
        # Индексирование
        self.doc_index[doc.doc_type].append(doc.doc_id)
        for tag in doc.tags:
            self.doc_index[f"tag:{tag}"].append(doc.doc_id)
        if doc.service_id:
            self.doc_index[f"service:{doc.service_id}"].append(doc.doc_id)
            
        return doc.doc_id
        
    def get_document(self, doc_id: str) -> Optional[Documentation]:
        """Получение документа"""
        return self.documents.get(doc_id)
        
    def search_documents(self, 
                         query: Optional[str] = None,
                         doc_type: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         service_id: Optional[str] = None) -> List[Documentation]:
        """Поиск документов"""
        results = list(self.documents.values())
        
        if query:
            query_lower = query.lower()
            results = [
                d for d in results
                if query_lower in d.title.lower() or query_lower in d.content.lower()
            ]
            
        if doc_type:
            results = [d for d in results if d.doc_type == doc_type]
            
        if tags:
            results = [d for d in results if any(t in d.tags for t in tags)]
            
        if service_id:
            results = [d for d in results if d.service_id == service_id]
            
        return sorted(results, key=lambda d: d.updated_at, reverse=True)
        
    def get_documentation_for_service(self, service_id: str) -> Dict[str, List[Documentation]]:
        """Получение документации для сервиса"""
        docs = self.search_documents(service_id=service_id)
        
        by_type = defaultdict(list)
        for doc in docs:
            by_type[doc.doc_type].append(doc)
            
        return dict(by_type)
        
    def sync_from_repository(self, repo_url: str, path: str) -> List[str]:
        """Синхронизация из репозитория (заглушка)"""
        # В реальности - клонирование репо и парсинг markdown файлов
        return []


class DeveloperMetricsCollector:
    """Сборщик метрик разработчиков"""
    
    def __init__(self):
        self.metrics: Dict[str, List[DeveloperMetrics]] = defaultdict(list)
        
    def collect_metrics(self, developer_id: str, 
                        period_start: datetime,
                        period_end: datetime,
                        data: Dict[str, Any]) -> DeveloperMetrics:
        """Сбор метрик"""
        metrics = DeveloperMetrics(
            developer_id=developer_id,
            period_start=period_start,
            period_end=period_end,
            commits_count=data.get("commits", 0),
            prs_opened=data.get("prs_opened", 0),
            prs_merged=data.get("prs_merged", 0),
            prs_reviewed=data.get("prs_reviewed", 0),
            code_coverage_avg=data.get("coverage", 0.0),
            bugs_introduced=data.get("bugs_introduced", 0),
            bugs_fixed=data.get("bugs_fixed", 0),
            story_points_completed=data.get("story_points", 0),
            tasks_completed=data.get("tasks", 0),
            avg_pr_cycle_time_hours=data.get("pr_cycle_time", 0.0)
        )
        
        self.metrics[developer_id].append(metrics)
        return metrics
        
    def get_developer_metrics(self, developer_id: str,
                               period: str = "weekly") -> Dict[str, Any]:
        """Получение метрик разработчика"""
        dev_metrics = self.metrics.get(developer_id, [])
        
        if not dev_metrics:
            return {"error": "No metrics found"}
            
        # Последний период
        latest = dev_metrics[-1]
        
        # Тренды (сравнение с предыдущим периодом)
        trends = {}
        if len(dev_metrics) > 1:
            previous = dev_metrics[-2]
            trends = {
                "commits": latest.commits_count - previous.commits_count,
                "prs_merged": latest.prs_merged - previous.prs_merged,
                "story_points": latest.story_points_completed - previous.story_points_completed
            }
            
        return {
            "developer_id": developer_id,
            "period": {
                "start": latest.period_start.isoformat(),
                "end": latest.period_end.isoformat()
            },
            "activity": {
                "commits": latest.commits_count,
                "prs_opened": latest.prs_opened,
                "prs_merged": latest.prs_merged,
                "prs_reviewed": latest.prs_reviewed
            },
            "quality": {
                "code_coverage": latest.code_coverage_avg,
                "bugs_introduced": latest.bugs_introduced,
                "bugs_fixed": latest.bugs_fixed
            },
            "velocity": {
                "story_points": latest.story_points_completed,
                "tasks_completed": latest.tasks_completed,
                "avg_pr_cycle_time_hours": latest.avg_pr_cycle_time_hours
            },
            "trends": trends
        }
        
    def get_team_metrics(self, team_members: List[str]) -> Dict[str, Any]:
        """Получение метрик команды"""
        team_metrics = []
        
        for dev_id in team_members:
            dev_metrics = self.metrics.get(dev_id, [])
            if dev_metrics:
                team_metrics.append(dev_metrics[-1])
                
        if not team_metrics:
            return {"error": "No metrics found"}
            
        return {
            "team_size": len(team_members),
            "period": "weekly",
            "totals": {
                "commits": sum(m.commits_count for m in team_metrics),
                "prs_merged": sum(m.prs_merged for m in team_metrics),
                "prs_reviewed": sum(m.prs_reviewed for m in team_metrics),
                "story_points": sum(m.story_points_completed for m in team_metrics)
            },
            "averages": {
                "commits_per_dev": sum(m.commits_count for m in team_metrics) / len(team_metrics),
                "prs_per_dev": sum(m.prs_merged for m in team_metrics) / len(team_metrics),
                "code_coverage": sum(m.code_coverage_avg for m in team_metrics) / len(team_metrics),
                "pr_cycle_time_hours": sum(m.avg_pr_cycle_time_hours for m in team_metrics) / len(team_metrics)
            }
        }


class PlatformAPI:
    """API платформы"""
    
    def __init__(self, catalog: ServiceCatalog, portal: SelfServicePortal,
                 golden_paths: GoldenPathManager, onboarding: DeveloperOnboarding,
                 docs: DocumentationHub, metrics: DeveloperMetricsCollector):
        self.catalog = catalog
        self.portal = portal
        self.golden_paths = golden_paths
        self.onboarding = onboarding
        self.docs = docs
        self.metrics = metrics
        
    def get_api_spec(self) -> Dict[str, Any]:
        """Спецификация API"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Internal Developer Platform API",
                "version": "1.0.0",
                "description": "API for developer self-service"
            },
            "paths": {
                "/services": {
                    "get": "List all services",
                    "post": "Create new service"
                },
                "/services/{id}": {
                    "get": "Get service details",
                    "put": "Update service",
                    "delete": "Delete service"
                },
                "/templates": {
                    "get": "List all templates"
                },
                "/requests": {
                    "get": "List requests",
                    "post": "Create new request"
                },
                "/requests/{id}": {
                    "get": "Get request status"
                },
                "/golden-paths": {
                    "get": "List golden paths"
                },
                "/docs": {
                    "get": "Search documentation"
                },
                "/metrics/{developer_id}": {
                    "get": "Get developer metrics"
                }
            }
        }


class InternalDeveloperPlatform:
    """Внутренняя платформа разработчика"""
    
    def __init__(self):
        self.catalog = ServiceCatalog()
        self.portal = SelfServicePortal(self.catalog)
        self.golden_paths = GoldenPathManager(self.catalog)
        self.onboarding = DeveloperOnboarding()
        self.docs = DocumentationHub()
        self.metrics = DeveloperMetricsCollector()
        self.api = PlatformAPI(
            self.catalog, self.portal, self.golden_paths,
            self.onboarding, self.docs, self.metrics
        )
        
    def initialize(self):
        """Инициализация платформы"""
        # Регистрация стандартных шаблонов
        templates = [
            ServiceTemplate(
                template_id="tmpl_python_api",
                name="Python REST API",
                description="Python FastAPI service with PostgreSQL",
                category=TemplateCategory.SERVICE,
                service_type=ServiceType.API,
                language="python",
                framework="fastapi",
                repo_template="https://github.com/org/python-api-template",
                includes_ci_cd=True,
                includes_monitoring=True,
                tags=["python", "api", "rest"]
            ),
            ServiceTemplate(
                template_id="tmpl_node_api",
                name="Node.js REST API",
                description="Node.js Express service",
                category=TemplateCategory.SERVICE,
                service_type=ServiceType.API,
                language="javascript",
                framework="express",
                repo_template="https://github.com/org/node-api-template",
                tags=["node", "javascript", "api"]
            ),
            ServiceTemplate(
                template_id="tmpl_react_frontend",
                name="React Frontend",
                description="React SPA with TypeScript",
                category=TemplateCategory.SERVICE,
                service_type=ServiceType.FRONTEND,
                language="typescript",
                framework="react",
                repo_template="https://github.com/org/react-template",
                tags=["react", "frontend", "typescript"]
            )
        ]
        
        for template in templates:
            self.catalog.register_template(template)
            
        # Регистрация workflows
        self.portal.register_workflow("create_service", self._workflow_create_service)
        self.portal.register_workflow("create_environment", self._workflow_create_environment)
        self.portal.register_workflow("request_access", self._workflow_request_access)
        
        # Правила одобрения
        self.portal.add_approval_rule({
            "request_type": "create_service",
            "environment": ["production"],
            "approvers": ["platform-team", "security-team"]
        })
        
        self.portal.add_approval_rule({
            "request_type": "create_environment",
            "tier": ["critical"],
            "approvers": ["platform-lead"]
        })
        
        # Создание golden paths
        self._create_default_golden_paths()
        
    def _create_default_golden_paths(self):
        """Создание стандартных golden paths"""
        paths = [
            GoldenPath(
                path_id="path_new_service",
                name="Create a New Service",
                description="Step-by-step guide to create and deploy a new microservice",
                use_case="Creating new microservices",
                target_audience="All developers",
                steps=[
                    {"id": "step1", "title": "Choose template", "description": "Select appropriate service template"},
                    {"id": "step2", "title": "Configure service", "description": "Set service name, team, and configuration"},
                    {"id": "step3", "title": "Create repository", "description": "Repository created from template"},
                    {"id": "step4", "title": "Set up CI/CD", "description": "Configure pipelines"},
                    {"id": "step5", "title": "Deploy to staging", "description": "Deploy first version to staging"},
                    {"id": "step6", "title": "Documentation", "description": "Create service documentation"}
                ],
                templates=["tmpl_python_api", "tmpl_node_api"],
                estimated_time="2-4 hours"
            ),
            GoldenPath(
                path_id="path_first_deployment",
                name="Your First Deployment",
                description="Guide for deploying your first change",
                use_case="First deployment for new developers",
                target_audience="Beginner developers",
                steps=[
                    {"id": "step1", "title": "Clone repository", "description": "Clone the service repo"},
                    {"id": "step2", "title": "Make changes", "description": "Implement your changes"},
                    {"id": "step3", "title": "Create PR", "description": "Open a pull request"},
                    {"id": "step4", "title": "Code review", "description": "Get code review"},
                    {"id": "step5", "title": "Merge and deploy", "description": "Merge and watch deployment"}
                ],
                estimated_time="1-2 hours"
            )
        ]
        
        for path in paths:
            self.golden_paths.create_path(path)
            
    async def _workflow_create_service(self, request: SelfServiceRequest) -> Dict[str, Any]:
        """Workflow создания сервиса"""
        params = request.parameters
        
        # Создание сервиса
        service = Service(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=params.get("name", "new-service"),
            description=params.get("description", ""),
            service_type=ServiceType(params.get("type", "microservice")),
            team=request.team,
            owner=request.requester
        )
        
        self.catalog.register_service(service)
        
        return {
            "service_id": service.service_id,
            "name": service.name,
            "repository": f"https://github.com/org/{service.name}",
            "created": True
        }
        
    async def _workflow_create_environment(self, request: SelfServiceRequest) -> Dict[str, Any]:
        """Workflow создания окружения"""
        params = request.parameters
        
        return {
            "environment": params.get("environment", "development"),
            "service_id": params.get("service_id"),
            "created": True,
            "url": f"https://{params.get('environment')}.example.com"
        }
        
    async def _workflow_request_access(self, request: SelfServiceRequest) -> Dict[str, Any]:
        """Workflow запроса доступа"""
        params = request.parameters
        
        return {
            "tool": params.get("tool"),
            "access_granted": True,
            "expires_at": (datetime.now() + timedelta(days=90)).isoformat()
        }
        
    def get_platform_dashboard(self) -> Dict[str, Any]:
        """Дашборд платформы"""
        catalog_stats = self.catalog.get_catalog_stats()
        
        # Запросы за последние 24 часа
        recent_requests = [
            r for r in self.portal.requests.values()
            if r.created_at > datetime.now() - timedelta(days=1)
        ]
        
        return {
            "catalog": catalog_stats,
            "requests": {
                "total_24h": len(recent_requests),
                "pending": len(self.portal.get_pending_requests()),
                "by_status": {
                    status.value: len([r for r in recent_requests if r.status == status])
                    for status in RequestStatus
                }
            },
            "golden_paths": {
                "total": len(self.golden_paths.paths)
            },
            "documentation": {
                "total_docs": len(self.docs.documents)
            },
            "onboarding": {
                "active": len([
                    d for d in self.onboarding.developers.values()
                    if d.onboarding_stage != OnboardingStage.COMPLETED
                ])
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 39: Platform Engineering")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = InternalDeveloperPlatform()
        platform.initialize()
        
        print("✓ Internal Developer Platform initialized")
        print(f"  Templates: {len(platform.catalog.templates)}")
        print(f"  Golden Paths: {len(platform.golden_paths.paths)}")
        
        # Регистрация сервисов
        services = [
            Service(
                service_id="svc_api_gateway",
                name="api-gateway",
                description="Main API Gateway",
                service_type=ServiceType.API,
                team="platform",
                tier="critical",
                sla="99.99%"
            ),
            Service(
                service_id="svc_user_service",
                name="user-service",
                description="User management service",
                service_type=ServiceType.MICROSERVICE,
                team="backend",
                dependencies=["svc_api_gateway"]
            )
        ]
        
        for service in services:
            platform.catalog.register_service(service)
            
        print(f"\n📦 Registered {len(services)} services")
        
        # Создание запроса на самообслуживание
        request = SelfServiceRequest(
            request_id=f"req_{uuid.uuid4().hex[:8]}",
            request_type="create_service",
            title="Create Order Service",
            description="New microservice for order management",
            requester="developer@company.com",
            team="backend",
            parameters={
                "name": "order-service",
                "type": "microservice",
                "template": "tmpl_python_api"
            }
        )
        
        request_id = await platform.portal.create_request(request)
        print(f"\n📝 Created request: {request_id}")
        
        status = platform.portal.get_request_status(request_id)
        print(f"   Status: {status['status']}")
        
        # Онбординг разработчика
        developer = Developer(
            developer_id="dev_001",
            name="John Doe",
            email="john.doe@company.com",
            team="backend",
            role="software_engineer"
        )
        
        platform.onboarding.start_onboarding(developer)
        print(f"\n👤 Started onboarding for {developer.name}")
        
        # Завершение задач онбординга
        platform.onboarding.complete_task("dev_001", "welcome_1")
        platform.onboarding.complete_task("dev_001", "account_1")
        
        onboarding_status = platform.onboarding.get_onboarding_status("dev_001")
        print(f"   Progress: {onboarding_status['progress']:.0f}%")
        print(f"   Stage: {onboarding_status['stage']}")
        
        # Добавление документации
        doc = Documentation(
            doc_id="doc_getting_started",
            title="Getting Started Guide",
            content="# Getting Started\n\nWelcome to the platform...",
            doc_type="guide",
            tags=["getting-started", "onboarding"],
            author="platform-team"
        )
        platform.docs.add_document(doc)
        
        print(f"\n📚 Documentation: {len(platform.docs.documents)} documents")
        
        # Сбор метрик
        platform.metrics.collect_metrics(
            "dev_001",
            datetime.now() - timedelta(days=7),
            datetime.now(),
            {
                "commits": 15,
                "prs_opened": 5,
                "prs_merged": 4,
                "prs_reviewed": 8,
                "coverage": 85.5,
                "story_points": 13,
                "pr_cycle_time": 4.5
            }
        )
        
        dev_metrics = platform.metrics.get_developer_metrics("dev_001")
        print(f"\n📊 Developer Metrics:")
        print(f"   Commits: {dev_metrics['activity']['commits']}")
        print(f"   PRs Merged: {dev_metrics['activity']['prs_merged']}")
        print(f"   Code Coverage: {dev_metrics['quality']['code_coverage']}%")
        
        # Дашборд платформы
        dashboard = platform.get_platform_dashboard()
        print(f"\n🎯 Platform Dashboard:")
        print(f"   Total Services: {dashboard['catalog']['total_services']}")
        print(f"   Templates: {dashboard['catalog']['total_templates']}")
        print(f"   Pending Requests: {dashboard['requests']['pending']}")
        print(f"   Active Onboarding: {dashboard['onboarding']['active']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Platform Engineering initialized successfully!")
    print("=" * 60)
