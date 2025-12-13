#!/usr/bin/env python3
"""
Server Init - Iteration 47: CI/CD Pipeline Engine
CI/CD Pipeline движок

Функционал:
- Pipeline Definition - определение пайплайнов
- Stage & Job Management - управление стадиями и задачами
- Parallel Execution - параллельное выполнение
- Artifact Management - управление артефактами
- Build Cache - кэширование сборки
- Environment Management - управление окружениями
- Deployment Strategies - стратегии деплоя
- Pipeline Analytics - аналитика пайплайнов
"""

import json
import asyncio
import hashlib
import time
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class PipelineStatus(Enum):
    """Статус пайплайна"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"


class JobStatus(Enum):
    """Статус задачи"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    SKIPPED = "skipped"
    MANUAL = "manual"


class TriggerType(Enum):
    """Тип триггера"""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE = "merge"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    API = "api"
    TAG = "tag"


class DeploymentStrategy(Enum):
    """Стратегия деплоя"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"
    A_B_TESTING = "a_b_testing"


class RunnerType(Enum):
    """Тип раннера"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SHELL = "shell"
    VM = "vm"


@dataclass
class Variable:
    """Переменная"""
    key: str
    value: str
    masked: bool = False
    protected: bool = False
    environment: Optional[str] = None


@dataclass
class Artifact:
    """Артефакт сборки"""
    artifact_id: str
    name: str
    path: str
    
    # Метаданные
    size: int = 0
    expire_at: Optional[datetime] = None
    
    # Связи
    job_id: str = ""
    pipeline_id: str = ""


@dataclass
class Cache:
    """Кэш сборки"""
    cache_id: str
    key: str
    paths: List[str] = field(default_factory=list)
    
    # Метаданные
    size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    
    # Политика
    policy: str = "pull-push"  # pull, push, pull-push


@dataclass
class JobLog:
    """Лог задачи"""
    entries: List[Dict[str, Any]] = field(default_factory=list)
    
    def append(self, message: str, level: str = "info"):
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        })


@dataclass
class Job:
    """Задача CI/CD"""
    job_id: str
    name: str
    stage: str
    
    # Скрипт
    script: List[str] = field(default_factory=list)
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)
    
    # Окружение
    image: str = ""
    services: List[str] = field(default_factory=list)
    
    # Зависимости
    needs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Артефакты
    artifacts: List[Artifact] = field(default_factory=list)
    artifact_paths: List[str] = field(default_factory=list)
    
    # Кэш
    cache: Optional[Cache] = None
    
    # Правила
    rules: List[Dict[str, Any]] = field(default_factory=list)
    only: List[str] = field(default_factory=list)
    except_: List[str] = field(default_factory=list)
    
    # Переменные
    variables: Dict[str, str] = field(default_factory=dict)
    
    # Настройки
    allow_failure: bool = False
    timeout: int = 3600  # seconds
    retry: int = 0
    parallel: int = 1
    when: str = "on_success"  # on_success, on_failure, always, manual
    
    # Состояние
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: float = 0.0
    
    # Раннер
    runner_id: Optional[str] = None
    
    # Логи
    log: JobLog = field(default_factory=JobLog)


@dataclass
class Stage:
    """Стадия пайплайна"""
    name: str
    jobs: List[Job] = field(default_factory=list)
    
    # Состояние
    status: PipelineStatus = PipelineStatus.PENDING
    
    # Настройки
    needs_approval: bool = False
    approved_by: Optional[str] = None


@dataclass
class Pipeline:
    """CI/CD Pipeline"""
    pipeline_id: str
    name: str
    
    # Источник
    project: str = ""
    ref: str = "main"
    sha: str = ""
    
    # Триггер
    trigger_type: TriggerType = TriggerType.PUSH
    triggered_by: str = ""
    
    # Стадии
    stages: List[Stage] = field(default_factory=list)
    
    # Переменные
    variables: Dict[str, Variable] = field(default_factory=dict)
    
    # Состояние
    status: PipelineStatus = PipelineStatus.PENDING
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration: float = 0.0
    
    # Артефакты
    artifacts: List[Artifact] = field(default_factory=list)
    
    # URL
    web_url: str = ""


@dataclass
class Environment:
    """Окружение деплоя"""
    env_id: str
    name: str
    
    # URL
    external_url: str = ""
    
    # Состояние
    state: str = "available"  # available, stopped
    
    # Деплоймент
    last_deployment_id: Optional[str] = None
    deployed_at: Optional[datetime] = None
    
    # Защита
    protected: bool = False
    required_approval: bool = False


@dataclass
class Deployment:
    """Деплоймент"""
    deployment_id: str
    environment: str
    
    # Пайплайн
    pipeline_id: str = ""
    job_id: str = ""
    
    # Стратегия
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    
    # Состояние
    status: str = "created"  # created, running, success, failed, canceled
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None
    
    # Rollback
    rollback_to: Optional[str] = None


@dataclass
class Runner:
    """CI/CD Runner"""
    runner_id: str
    name: str
    
    # Тип
    runner_type: RunnerType = RunnerType.DOCKER
    
    # Настройки
    executor: str = "docker"
    tags: List[str] = field(default_factory=list)
    
    # Состояние
    status: str = "online"  # online, offline, paused
    
    # Метрики
    jobs_count: int = 0
    current_job: Optional[str] = None
    
    # Метаданные
    registered_at: datetime = field(default_factory=datetime.now)
    last_contact: datetime = field(default_factory=datetime.now)


class PipelineParser:
    """Парсер пайплайнов"""
    
    def parse_yaml(self, config: Dict[str, Any]) -> Pipeline:
        """Парсинг конфигурации пайплайна"""
        pipeline = Pipeline(
            pipeline_id=f"pipeline_{uuid.uuid4().hex[:8]}",
            name=config.get("name", "pipeline")
        )
        
        # Парсинг стадий
        stage_names = config.get("stages", ["build", "test", "deploy"])
        stages: Dict[str, Stage] = {}
        
        for stage_name in stage_names:
            stages[stage_name] = Stage(name=stage_name)
            
        # Парсинг задач
        for job_name, job_config in config.items():
            if job_name in ["stages", "variables", "default", "workflow"]:
                continue
                
            if not isinstance(job_config, dict):
                continue
                
            stage_name = job_config.get("stage", "test")
            
            job = Job(
                job_id=f"job_{uuid.uuid4().hex[:8]}",
                name=job_name,
                stage=stage_name,
                script=job_config.get("script", []),
                before_script=job_config.get("before_script", []),
                after_script=job_config.get("after_script", []),
                image=job_config.get("image", ""),
                needs=job_config.get("needs", []),
                variables=job_config.get("variables", {}),
                allow_failure=job_config.get("allow_failure", False),
                when=job_config.get("when", "on_success"),
                artifact_paths=job_config.get("artifacts", {}).get("paths", [])
            )
            
            if stage_name in stages:
                stages[stage_name].jobs.append(job)
                
        pipeline.stages = list(stages.values())
        
        # Парсинг переменных
        for key, value in config.get("variables", {}).items():
            pipeline.variables[key] = Variable(key=key, value=str(value))
            
        return pipeline


class JobExecutor:
    """Исполнитель задач"""
    
    def __init__(self):
        self.runners: Dict[str, Runner] = {}
        
    def register_runner(self, runner: Runner):
        """Регистрация раннера"""
        self.runners[runner.runner_id] = runner
        
    def find_available_runner(self, job: Job) -> Optional[Runner]:
        """Поиск доступного раннера"""
        for runner in self.runners.values():
            if runner.status == "online" and not runner.current_job:
                return runner
        return None
        
    async def execute_job(self, job: Job, 
                           variables: Dict[str, Variable]) -> JobStatus:
        """Выполнение задачи"""
        runner = self.find_available_runner(job)
        
        if not runner:
            job.log.append("No available runner", "warning")
            return JobStatus.PENDING
            
        job.runner_id = runner.runner_id
        runner.current_job = job.job_id
        runner.jobs_count += 1
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        job.log.append(f"Job started on runner {runner.name}", "info")
        
        try:
            # Before script
            for cmd in job.before_script:
                job.log.append(f"$ {cmd}", "info")
                await asyncio.sleep(0.02)
                
            # Main script
            for cmd in job.script:
                job.log.append(f"$ {cmd}", "info")
                await asyncio.sleep(0.05)
                
                # Симуляция вывода команды
                job.log.append(f"Output: executed {cmd}", "info")
                
            # After script
            for cmd in job.after_script:
                job.log.append(f"$ {cmd}", "info")
                await asyncio.sleep(0.02)
                
            # Генерация артефактов
            for path in job.artifact_paths:
                artifact = Artifact(
                    artifact_id=f"artifact_{uuid.uuid4().hex[:8]}",
                    name=os.path.basename(path),
                    path=path,
                    job_id=job.job_id,
                    size=random.randint(1000, 1000000)
                )
                job.artifacts.append(artifact)
                job.log.append(f"Artifact created: {path}", "info")
                
            job.status = JobStatus.SUCCESS
            job.log.append("Job succeeded", "info")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.log.append(f"Job failed: {str(e)}", "error")
            
        finally:
            job.finished_at = datetime.now()
            job.duration = (job.finished_at - job.started_at).total_seconds()
            runner.current_job = None
            
        return job.status


class PipelineEngine:
    """Движок CI/CD Pipeline"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.parser = PipelineParser()
        self.executor = JobExecutor()
        self.environments: Dict[str, Environment] = {}
        self.deployments: Dict[str, Deployment] = {}
        
        # Кэш
        self.cache_store: Dict[str, Cache] = {}
        
        # Артефакты
        self.artifact_store: Dict[str, Artifact] = {}
        
        # История
        self.pipeline_history: List[Dict[str, Any]] = []
        
    def create_pipeline(self, config: Dict[str, Any],
                         project: str = "",
                         ref: str = "main",
                         trigger_type: TriggerType = TriggerType.PUSH) -> Pipeline:
        """Создание пайплайна"""
        pipeline = self.parser.parse_yaml(config)
        pipeline.project = project
        pipeline.ref = ref
        pipeline.sha = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        pipeline.trigger_type = trigger_type
        
        self.pipelines[pipeline.pipeline_id] = pipeline
        
        return pipeline
        
    async def run_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Запуск пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return {"error": "Pipeline not found"}
            
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.now()
        
        results = {
            "pipeline_id": pipeline_id,
            "stages": []
        }
        
        # Выполнение стадий последовательно
        for stage in pipeline.stages:
            stage_result = await self._run_stage(stage, pipeline)
            results["stages"].append(stage_result)
            
            if stage.status == PipelineStatus.FAILED:
                pipeline.status = PipelineStatus.FAILED
                break
                
        # Обновление статуса
        if pipeline.status == PipelineStatus.RUNNING:
            pipeline.status = PipelineStatus.SUCCESS
            
        pipeline.finished_at = datetime.now()
        pipeline.duration = (pipeline.finished_at - pipeline.started_at).total_seconds()
        
        # Сбор артефактов
        for stage in pipeline.stages:
            for job in stage.jobs:
                pipeline.artifacts.extend(job.artifacts)
                
        # Сохранение в историю
        self.pipeline_history.append({
            "pipeline_id": pipeline_id,
            "status": pipeline.status.value,
            "duration": pipeline.duration,
            "timestamp": datetime.now().isoformat()
        })
        
        results["status"] = pipeline.status.value
        results["duration"] = pipeline.duration
        
        return results
        
    async def _run_stage(self, stage: Stage, 
                          pipeline: Pipeline) -> Dict[str, Any]:
        """Выполнение стадии"""
        stage.status = PipelineStatus.RUNNING
        
        # Группировка задач по зависимостям
        jobs_without_deps = [j for j in stage.jobs if not j.needs]
        jobs_with_deps = [j for j in stage.jobs if j.needs]
        
        results = {
            "stage": stage.name,
            "jobs": []
        }
        
        # Параллельное выполнение независимых задач
        if jobs_without_deps:
            tasks = [
                self.executor.execute_job(job, pipeline.variables)
                for job in jobs_without_deps
            ]
            await asyncio.gather(*tasks)
            
            for job in jobs_without_deps:
                results["jobs"].append({
                    "name": job.name,
                    "status": job.status.value,
                    "duration": job.duration
                })
                
        # Выполнение задач с зависимостями
        for job in jobs_with_deps:
            # Проверка зависимостей
            deps_ok = all(
                self._get_job_by_name(stage, dep).status == JobStatus.SUCCESS
                for dep in job.needs
                if self._get_job_by_name(stage, dep)
            )
            
            if deps_ok:
                await self.executor.execute_job(job, pipeline.variables)
            else:
                job.status = JobStatus.SKIPPED
                
            results["jobs"].append({
                "name": job.name,
                "status": job.status.value,
                "duration": job.duration
            })
            
        # Определение статуса стадии
        failed_jobs = [j for j in stage.jobs if j.status == JobStatus.FAILED and not j.allow_failure]
        
        if failed_jobs:
            stage.status = PipelineStatus.FAILED
        else:
            stage.status = PipelineStatus.SUCCESS
            
        results["status"] = stage.status.value
        
        return results
        
    def _get_job_by_name(self, stage: Stage, name: str) -> Optional[Job]:
        """Получение задачи по имени"""
        for job in stage.jobs:
            if job.name == name:
                return job
        return None
        
    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Отмена пайплайна"""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return False
            
        pipeline.status = PipelineStatus.CANCELED
        pipeline.finished_at = datetime.now()
        
        for stage in pipeline.stages:
            if stage.status == PipelineStatus.RUNNING:
                stage.status = PipelineStatus.CANCELED
                for job in stage.jobs:
                    if job.status == JobStatus.RUNNING:
                        job.status = JobStatus.CANCELED
                        
        return True
        
    async def retry_pipeline(self, pipeline_id: str) -> Optional[str]:
        """Повторный запуск пайплайна"""
        old_pipeline = self.pipelines.get(pipeline_id)
        if not old_pipeline:
            return None
            
        # Создание нового пайплайна на основе старого
        new_pipeline = Pipeline(
            pipeline_id=f"pipeline_{uuid.uuid4().hex[:8]}",
            name=old_pipeline.name,
            project=old_pipeline.project,
            ref=old_pipeline.ref,
            trigger_type=TriggerType.API,
            stages=old_pipeline.stages  # Пересоздание стадий нужно
        )
        
        self.pipelines[new_pipeline.pipeline_id] = new_pipeline
        
        return new_pipeline.pipeline_id
        
    def create_environment(self, name: str, 
                            external_url: str = "") -> Environment:
        """Создание окружения"""
        env = Environment(
            env_id=f"env_{uuid.uuid4().hex[:8]}",
            name=name,
            external_url=external_url
        )
        
        self.environments[env.env_id] = env
        
        return env
        
    async def deploy(self, pipeline_id: str, environment: str,
                      strategy: DeploymentStrategy = DeploymentStrategy.ROLLING) -> Deployment:
        """Создание деплоймента"""
        deployment = Deployment(
            deployment_id=f"deploy_{uuid.uuid4().hex[:8]}",
            environment=environment,
            pipeline_id=pipeline_id,
            strategy=strategy
        )
        
        deployment.status = "running"
        
        # Симуляция деплоя
        await asyncio.sleep(0.2)
        
        deployment.status = "success"
        deployment.deployed_at = datetime.now()
        
        self.deployments[deployment.deployment_id] = deployment
        
        # Обновление окружения
        for env in self.environments.values():
            if env.name == environment:
                env.last_deployment_id = deployment.deployment_id
                env.deployed_at = deployment.deployed_at
                break
                
        return deployment
        
    async def rollback(self, deployment_id: str) -> Optional[Deployment]:
        """Откат деплоймента"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return None
            
        # Поиск предыдущего успешного деплоймента
        env_deployments = [
            d for d in self.deployments.values()
            if d.environment == deployment.environment
            and d.status == "success"
            and d.deployment_id != deployment_id
        ]
        
        if not env_deployments:
            return None
            
        # Последний успешный
        previous = max(env_deployments, key=lambda x: x.deployed_at or datetime.min)
        
        # Создание rollback deployment
        rollback = Deployment(
            deployment_id=f"deploy_{uuid.uuid4().hex[:8]}",
            environment=deployment.environment,
            rollback_to=previous.deployment_id
        )
        
        rollback.status = "running"
        await asyncio.sleep(0.1)
        rollback.status = "success"
        rollback.deployed_at = datetime.now()
        
        self.deployments[rollback.deployment_id] = rollback
        
        return rollback
        
    def get_pipeline_analytics(self) -> Dict[str, Any]:
        """Аналитика пайплайнов"""
        total = len(self.pipeline_history)
        
        if total == 0:
            return {"total": 0}
            
        success = len([p for p in self.pipeline_history if p["status"] == "success"])
        failed = len([p for p in self.pipeline_history if p["status"] == "failed"])
        
        durations = [p["duration"] for p in self.pipeline_history if p["duration"] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0,
            "average_duration": round(avg_duration, 2),
            "pipelines_per_day": len([
                p for p in self.pipeline_history
                if datetime.fromisoformat(p["timestamp"]).date() == datetime.now().date()
            ])
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        return {
            "pipelines": len(self.pipelines),
            "environments": len(self.environments),
            "deployments": len(self.deployments),
            "runners": len(self.executor.runners),
            "online_runners": len([
                r for r in self.executor.runners.values()
                if r.status == "online"
            ]),
            "cached_items": len(self.cache_store),
            "artifacts": len(self.artifact_store)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 47: CI/CD Pipeline Engine")
    print("=" * 60)
    
    async def demo():
        # Создание движка
        engine = PipelineEngine()
        print("✓ CI/CD Pipeline Engine created")
        
        # Регистрация раннеров
        print("\n🖥️ Registering runners...")
        
        runner1 = Runner(
            runner_id="runner_001",
            name="docker-runner-1",
            runner_type=RunnerType.DOCKER,
            tags=["docker", "linux"]
        )
        engine.executor.register_runner(runner1)
        print(f"  ✓ Registered: {runner1.name}")
        
        runner2 = Runner(
            runner_id="runner_002",
            name="docker-runner-2",
            runner_type=RunnerType.DOCKER,
            tags=["docker", "linux"]
        )
        engine.executor.register_runner(runner2)
        print(f"  ✓ Registered: {runner2.name}")
        
        # Создание окружений
        print("\n🌍 Creating environments...")
        
        staging = engine.create_environment(
            name="staging",
            external_url="https://staging.example.com"
        )
        print(f"  ✓ Created: {staging.name}")
        
        production = engine.create_environment(
            name="production",
            external_url="https://example.com"
        )
        production.protected = True
        production.required_approval = True
        print(f"  ✓ Created: {production.name} (protected)")
        
        # Конфигурация пайплайна
        pipeline_config = {
            "name": "web-app-pipeline",
            "stages": ["build", "test", "deploy"],
            "variables": {
                "DOCKER_IMAGE": "myapp:latest",
                "NODE_ENV": "production"
            },
            "build": {
                "stage": "build",
                "image": "node:18",
                "script": [
                    "npm install",
                    "npm run build"
                ],
                "artifacts": {
                    "paths": ["dist/", "node_modules/"]
                }
            },
            "unit-tests": {
                "stage": "test",
                "image": "node:18",
                "needs": ["build"],
                "script": [
                    "npm run test:unit"
                ]
            },
            "integration-tests": {
                "stage": "test",
                "image": "node:18",
                "needs": ["build"],
                "script": [
                    "npm run test:integration"
                ],
                "allow_failure": True
            },
            "deploy-staging": {
                "stage": "deploy",
                "image": "kubectl:latest",
                "script": [
                    "kubectl apply -f k8s/staging/"
                ],
                "when": "on_success"
            }
        }
        
        # Создание и запуск пайплайна
        print("\n🚀 Creating pipeline...")
        
        pipeline = engine.create_pipeline(
            config=pipeline_config,
            project="web-app",
            ref="main",
            trigger_type=TriggerType.PUSH
        )
        print(f"  Pipeline ID: {pipeline.pipeline_id}")
        print(f"  Stages: {[s.name for s in pipeline.stages]}")
        print(f"  Jobs: {sum(len(s.jobs) for s in pipeline.stages)}")
        
        # Запуск пайплайна
        print("\n▶️ Running pipeline...")
        
        result = await engine.run_pipeline(pipeline.pipeline_id)
        
        print(f"\n📊 Pipeline Results:")
        print(f"  Status: {result['status']}")
        print(f"  Duration: {result['duration']:.2f}s")
        
        for stage_result in result["stages"]:
            print(f"\n  Stage: {stage_result['stage']} ({stage_result['status']})")
            for job in stage_result["jobs"]:
                status_icon = "✓" if job["status"] == "success" else "✗"
                print(f"    {status_icon} {job['name']}: {job['status']} ({job['duration']:.2f}s)")
                
        # Просмотр логов
        print("\n📝 Job Logs (build):")
        
        for stage in pipeline.stages:
            for job in stage.jobs:
                if job.name == "build":
                    for entry in job.log.entries[:5]:
                        print(f"    [{entry['level']}] {entry['message']}")
                        
        # Артефакты
        print("\n📦 Pipeline Artifacts:")
        
        for artifact in pipeline.artifacts[:3]:
            print(f"  - {artifact.name}: {artifact.size} bytes")
            
        # Деплой
        print("\n🚢 Deploying to staging...")
        
        deployment = await engine.deploy(
            pipeline_id=pipeline.pipeline_id,
            environment="staging",
            strategy=DeploymentStrategy.ROLLING
        )
        print(f"  Deployment ID: {deployment.deployment_id}")
        print(f"  Status: {deployment.status}")
        print(f"  Strategy: {deployment.strategy.value}")
        
        # Второй пайплайн для статистики
        print("\n📈 Running more pipelines for analytics...")
        
        for i in range(3):
            p = engine.create_pipeline(
                config=pipeline_config,
                project="web-app",
                ref="main"
            )
            await engine.run_pipeline(p.pipeline_id)
            
        # Аналитика
        analytics = engine.get_pipeline_analytics()
        print(f"\n📊 Pipeline Analytics:")
        print(f"  Total pipelines: {analytics['total']}")
        print(f"  Success rate: {analytics['success_rate']}%")
        print(f"  Average duration: {analytics['average_duration']}s")
        
        # Статистика
        stats = engine.get_statistics()
        print(f"\n📈 Engine Statistics:")
        print(f"  Pipelines: {stats['pipelines']}")
        print(f"  Environments: {stats['environments']}")
        print(f"  Deployments: {stats['deployments']}")
        print(f"  Runners: {stats['runners']} ({stats['online_runners']} online)")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("CI/CD Pipeline Engine initialized!")
    print("=" * 60)
