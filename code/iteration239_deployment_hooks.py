#!/usr/bin/env python3
"""
Server Init - Iteration 239: Deployment Hooks Platform
Платформа хуков деплоя

Функционал:
- Pre-Deploy Hooks - хуки до деплоя
- Post-Deploy Hooks - хуки после деплоя
- Rollback Hooks - хуки при откате
- Health Check Hooks - хуки проверки здоровья
- Notification Hooks - хуки уведомлений
- Custom Scripts - кастомные скрипты
- Webhook Integration - интеграция с вебхуками
- Hook Chains - цепочки хуков
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import json


class HookType(Enum):
    """Тип хука"""
    PRE_DEPLOY = "pre_deploy"
    POST_DEPLOY = "post_deploy"
    PRE_ROLLBACK = "pre_rollback"
    POST_ROLLBACK = "post_rollback"
    HEALTH_CHECK = "health_check"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class HookStatus(Enum):
    """Статус хука"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ExecutionMode(Enum):
    """Режим выполнения"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class HookScript:
    """Скрипт хука"""
    script_id: str
    name: str = ""
    
    # Content
    script_type: str = "bash"  # bash, python, powershell, webhook
    content: str = ""
    
    # Webhook specific
    webhook_url: str = ""
    webhook_method: str = "POST"
    webhook_headers: Dict[str, str] = field(default_factory=dict)
    
    # Timeout
    timeout_seconds: int = 300
    
    # Retry
    retry_count: int = 0
    retry_delay: int = 5


@dataclass
class Hook:
    """Хук деплоя"""
    hook_id: str
    name: str = ""
    description: str = ""
    
    # Type
    hook_type: HookType = HookType.PRE_DEPLOY
    
    # Script
    script_id: str = ""
    
    # Order
    priority: int = 100  # Lower = runs first
    
    # Conditions
    environments: List[str] = field(default_factory=list)  # Empty = all
    services: List[str] = field(default_factory=list)  # Empty = all
    
    # Settings
    fail_on_error: bool = True
    continue_on_failure: bool = False
    
    # Active
    is_enabled: bool = True
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HookExecution:
    """Выполнение хука"""
    execution_id: str
    hook_id: str = ""
    deployment_id: str = ""
    
    # Status
    status: HookStatus = HookStatus.PENDING
    
    # Output
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    
    # Times
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    
    # Retries
    attempt: int = 1


@dataclass
class HookChain:
    """Цепочка хуков"""
    chain_id: str
    name: str = ""
    
    # Hooks (ordered list of hook_ids)
    hooks: List[str] = field(default_factory=list)
    
    # Execution mode
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    
    # Active
    is_enabled: bool = True


@dataclass
class Deployment:
    """Деплой для контекста хуков"""
    deployment_id: str
    service: str = ""
    environment: str = ""
    version: str = ""
    
    # Status
    status: str = "pending"  # pending, running, success, failed, rolled_back
    
    # Hooks
    pre_hooks_completed: bool = False
    post_hooks_completed: bool = False
    
    # Times
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class HookTemplate:
    """Шаблон хука"""
    template_id: str
    name: str = ""
    description: str = ""
    
    # Template
    hook_type: HookType = HookType.PRE_DEPLOY
    script_template: str = ""
    
    # Variables
    variables: List[str] = field(default_factory=list)


class DeploymentHooksPlatform:
    """Платформа хуков деплоя"""
    
    def __init__(self):
        self.scripts: Dict[str, HookScript] = {}
        self.hooks: Dict[str, Hook] = {}
        self.chains: Dict[str, HookChain] = {}
        self.executions: List[HookExecution] = []
        self.deployments: Dict[str, Deployment] = {}
        self.templates: Dict[str, HookTemplate] = {}
        
    def create_script(self, name: str, script_type: str = "bash",
                     content: str = "", webhook_url: str = "",
                     timeout: int = 300) -> HookScript:
        """Создание скрипта"""
        script = HookScript(
            script_id=f"scr_{uuid.uuid4().hex[:8]}",
            name=name,
            script_type=script_type,
            content=content,
            webhook_url=webhook_url,
            timeout_seconds=timeout
        )
        
        self.scripts[script.script_id] = script
        return script
        
    def create_hook(self, name: str, hook_type: HookType,
                   script_id: str, priority: int = 100,
                   environments: List[str] = None,
                   services: List[str] = None,
                   fail_on_error: bool = True) -> Hook:
        """Создание хука"""
        hook = Hook(
            hook_id=f"hook_{uuid.uuid4().hex[:8]}",
            name=name,
            hook_type=hook_type,
            script_id=script_id,
            priority=priority,
            environments=environments or [],
            services=services or [],
            fail_on_error=fail_on_error
        )
        
        self.hooks[hook.hook_id] = hook
        return hook
        
    def create_chain(self, name: str, hook_ids: List[str],
                    mode: ExecutionMode = ExecutionMode.SEQUENTIAL) -> HookChain:
        """Создание цепочки хуков"""
        chain = HookChain(
            chain_id=f"chain_{uuid.uuid4().hex[:8]}",
            name=name,
            hooks=hook_ids,
            mode=mode
        )
        
        self.chains[chain.chain_id] = chain
        return chain
        
    def create_deployment(self, service: str, environment: str,
                         version: str) -> Deployment:
        """Создание деплоя"""
        deployment = Deployment(
            deployment_id=f"dep_{uuid.uuid4().hex[:8]}",
            service=service,
            environment=environment,
            version=version
        )
        
        self.deployments[deployment.deployment_id] = deployment
        return deployment
        
    def get_applicable_hooks(self, hook_type: HookType,
                            service: str, environment: str) -> List[Hook]:
        """Получение применимых хуков"""
        applicable = []
        
        for hook in self.hooks.values():
            if not hook.is_enabled:
                continue
                
            if hook.hook_type != hook_type:
                continue
                
            # Check environment filter
            if hook.environments and environment not in hook.environments:
                continue
                
            # Check service filter
            if hook.services and service not in hook.services:
                continue
                
            applicable.append(hook)
            
        # Sort by priority
        applicable.sort(key=lambda h: h.priority)
        
        return applicable
        
    def execute_hook(self, hook_id: str, deployment_id: str) -> HookExecution:
        """Выполнение хука"""
        hook = self.hooks.get(hook_id)
        deployment = self.deployments.get(deployment_id)
        
        execution = HookExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            hook_id=hook_id,
            deployment_id=deployment_id,
            started_at=datetime.now()
        )
        
        execution.status = HookStatus.RUNNING
        
        # Simulate execution
        script = self.scripts.get(hook.script_id) if hook else None
        
        # Random execution time (50-500ms)
        execution.duration_ms = random.randint(50, 500)
        
        # 95% success rate
        if random.random() > 0.05:
            execution.status = HookStatus.SUCCESS
            execution.exit_code = 0
            execution.stdout = f"Hook {hook.name if hook else 'unknown'} executed successfully"
        else:
            execution.status = HookStatus.FAILED
            execution.exit_code = 1
            execution.stderr = "Simulated hook failure"
            
        execution.completed_at = datetime.now()
        
        self.executions.append(execution)
        return execution
        
    def run_pre_deploy_hooks(self, deployment_id: str) -> List[HookExecution]:
        """Запуск pre-deploy хуков"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return []
            
        hooks = self.get_applicable_hooks(
            HookType.PRE_DEPLOY,
            deployment.service,
            deployment.environment
        )
        
        results = []
        for hook in hooks:
            exec_result = self.execute_hook(hook.hook_id, deployment_id)
            results.append(exec_result)
            
            # Stop on failure if configured
            if exec_result.status == HookStatus.FAILED and hook.fail_on_error:
                if not hook.continue_on_failure:
                    break
                    
        deployment.pre_hooks_completed = all(
            e.status == HookStatus.SUCCESS for e in results
        )
        
        return results
        
    def run_post_deploy_hooks(self, deployment_id: str) -> List[HookExecution]:
        """Запуск post-deploy хуков"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return []
            
        hooks = self.get_applicable_hooks(
            HookType.POST_DEPLOY,
            deployment.service,
            deployment.environment
        )
        
        results = []
        for hook in hooks:
            exec_result = self.execute_hook(hook.hook_id, deployment_id)
            results.append(exec_result)
            
        deployment.post_hooks_completed = True
        
        return results
        
    def run_chain(self, chain_id: str, deployment_id: str) -> List[HookExecution]:
        """Запуск цепочки хуков"""
        chain = self.chains.get(chain_id)
        if not chain:
            return []
            
        results = []
        
        if chain.mode == ExecutionMode.SEQUENTIAL:
            for hook_id in chain.hooks:
                exec_result = self.execute_hook(hook_id, deployment_id)
                results.append(exec_result)
                
                if exec_result.status == HookStatus.FAILED:
                    hook = self.hooks.get(hook_id)
                    if hook and hook.fail_on_error:
                        break
                        
        elif chain.mode == ExecutionMode.PARALLEL:
            # In real implementation, these would run in parallel
            for hook_id in chain.hooks:
                exec_result = self.execute_hook(hook_id, deployment_id)
                results.append(exec_result)
                
        return results
        
    def create_template(self, name: str, hook_type: HookType,
                       script_template: str,
                       variables: List[str] = None) -> HookTemplate:
        """Создание шаблона хука"""
        template = HookTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            hook_type=hook_type,
            script_template=script_template,
            variables=variables or []
        )
        
        self.templates[template.template_id] = template
        return template
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        executions = self.executions
        
        successful = [e for e in executions if e.status == HookStatus.SUCCESS]
        failed = [e for e in executions if e.status == HookStatus.FAILED]
        
        # Average duration
        if executions:
            avg_duration = sum(e.duration_ms for e in executions) / len(executions)
        else:
            avg_duration = 0
            
        # By type
        by_type = {}
        for hook in self.hooks.values():
            t = hook.hook_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        return {
            "total_scripts": len(self.scripts),
            "total_hooks": len(self.hooks),
            "total_chains": len(self.chains),
            "total_executions": len(executions),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": (len(successful) / len(executions) * 100) if executions else 0,
            "avg_duration_ms": avg_duration,
            "hooks_by_type": by_type
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 239: Deployment Hooks Platform")
    print("=" * 60)
    
    platform = DeploymentHooksPlatform()
    print("✓ Deployment Hooks Platform created")
    
    # Create scripts
    print("\n📜 Creating Hook Scripts...")
    
    scripts_config = [
        ("Database Migration", "bash", "#!/bin/bash\necho 'Running migrations...'\n./migrate.sh"),
        ("Cache Warmup", "python", "import cache\ncache.warmup()"),
        ("Slack Notification", "webhook", ""),
        ("Health Check", "bash", "#!/bin/bash\ncurl -f http://localhost:8080/health"),
        ("Config Backup", "bash", "#!/bin/bash\ncp config.yml config.yml.bak"),
        ("Load Balancer Update", "bash", "#!/bin/bash\nhaproxy -sf $(cat /var/run/haproxy.pid)"),
        ("Smoke Tests", "bash", "#!/bin/bash\n./run-smoke-tests.sh"),
        ("Metrics Reset", "python", "import metrics\nmetrics.reset_counters()"),
    ]
    
    scripts = []
    for name, stype, content in scripts_config:
        webhook_url = "https://hooks.slack.com/services/xxx" if stype == "webhook" else ""
        script = platform.create_script(name, stype, content, webhook_url)
        scripts.append(script)
        
        type_icons = {"bash": "🐚", "python": "🐍", "webhook": "🔗", "powershell": "💠"}
        icon = type_icons.get(stype, "📜")
        print(f"  {icon} {name} ({stype})")
        
    # Create hooks
    print("\n🪝 Creating Deployment Hooks...")
    
    hooks_config = [
        ("Run Database Migrations", HookType.PRE_DEPLOY, scripts[0].script_id, 10, ["prod", "staging"], []),
        ("Backup Config", HookType.PRE_DEPLOY, scripts[4].script_id, 20, [], []),
        ("Update Load Balancer", HookType.POST_DEPLOY, scripts[5].script_id, 10, ["prod"], []),
        ("Run Smoke Tests", HookType.POST_DEPLOY, scripts[6].script_id, 20, [], []),
        ("Notify Slack", HookType.POST_DEPLOY, scripts[2].script_id, 100, [], []),
        ("Health Check", HookType.HEALTH_CHECK, scripts[3].script_id, 10, [], []),
        ("Warmup Cache", HookType.POST_DEPLOY, scripts[1].script_id, 30, [], ["api-service"]),
        ("Reset Metrics", HookType.PRE_DEPLOY, scripts[7].script_id, 50, [], []),
    ]
    
    hooks = []
    for name, htype, script_id, priority, envs, services in hooks_config:
        hook = platform.create_hook(name, htype, script_id, priority, envs, services)
        hooks.append(hook)
        
        type_icons = {
            HookType.PRE_DEPLOY: "⬅️",
            HookType.POST_DEPLOY: "➡️",
            HookType.HEALTH_CHECK: "💓",
            HookType.NOTIFICATION: "📢"
        }
        icon = type_icons.get(htype, "🪝")
        print(f"  {icon} {name} (priority: {priority})")
        
    # Create hook chains
    print("\n🔗 Creating Hook Chains...")
    
    pre_deploy_hooks = [h.hook_id for h in hooks if h.hook_type == HookType.PRE_DEPLOY]
    post_deploy_hooks = [h.hook_id for h in hooks if h.hook_type == HookType.POST_DEPLOY]
    
    chains = [
        platform.create_chain("Pre-Deploy Chain", pre_deploy_hooks, ExecutionMode.SEQUENTIAL),
        platform.create_chain("Post-Deploy Chain", post_deploy_hooks, ExecutionMode.SEQUENTIAL),
    ]
    
    for chain in chains:
        print(f"  ⛓️ {chain.name} ({len(chain.hooks)} hooks, {chain.mode.value})")
        
    # Create templates
    print("\n📋 Creating Hook Templates...")
    
    templates = [
        platform.create_template(
            "Database Migration Template",
            HookType.PRE_DEPLOY,
            "#!/bin/bash\ncd {{PROJECT_DIR}}\n./migrate.sh --env={{ENVIRONMENT}}",
            ["PROJECT_DIR", "ENVIRONMENT"]
        ),
        platform.create_template(
            "Slack Notification Template",
            HookType.NOTIFICATION,
            '{"text": "Deployment {{VERSION}} to {{ENVIRONMENT}} completed"}',
            ["VERSION", "ENVIRONMENT"]
        ),
    ]
    
    for tmpl in templates:
        print(f"  📋 {tmpl.name} ({len(tmpl.variables)} vars)")
        
    # Simulate deployments
    print("\n🚀 Simulating Deployments...")
    
    deployments_config = [
        ("api-service", "prod", "v2.1.0"),
        ("web-frontend", "staging", "v3.0.0-beta"),
        ("worker-service", "prod", "v1.5.2"),
    ]
    
    deployments = []
    for service, env, version in deployments_config:
        deployment = platform.create_deployment(service, env, version)
        deployments.append(deployment)
        print(f"\n  📦 {service} {version} -> {env}")
        
        # Run pre-deploy hooks
        print("    Pre-Deploy Hooks:")
        pre_results = platform.run_pre_deploy_hooks(deployment.deployment_id)
        for result in pre_results:
            hook = platform.hooks.get(result.hook_id)
            hook_name = hook.name if hook else "unknown"
            status_icon = "✅" if result.status == HookStatus.SUCCESS else "❌"
            print(f"      {status_icon} {hook_name} ({result.duration_ms}ms)")
            
        # Simulate deployment
        deployment.status = "running"
        
        # Run post-deploy hooks
        print("    Post-Deploy Hooks:")
        post_results = platform.run_post_deploy_hooks(deployment.deployment_id)
        for result in post_results:
            hook = platform.hooks.get(result.hook_id)
            hook_name = hook.name if hook else "unknown"
            status_icon = "✅" if result.status == HookStatus.SUCCESS else "❌"
            print(f"      {status_icon} {hook_name} ({result.duration_ms}ms)")
            
        deployment.status = "success" if deployment.pre_hooks_completed else "failed"
        deployment.completed_at = datetime.now()
        
    # Display hooks
    print("\n🪝 Deployment Hooks:")
    
    print("\n  ┌────────────────────────────────┬────────────────┬──────────┬─────────┐")
    print("  │ Hook Name                      │ Type           │ Priority │ Status  │")
    print("  ├────────────────────────────────┼────────────────┼──────────┼─────────┤")
    
    for hook in platform.hooks.values():
        name = hook.name[:30].ljust(30)
        htype = hook.hook_type.value[:14].ljust(14)
        priority = str(hook.priority)[:8].ljust(8)
        status = "🟢" if hook.is_enabled else "🔴"
        
        print(f"  │ {name} │ {htype} │ {priority} │ {status:7s} │")
        
    print("  └────────────────────────────────┴────────────────┴──────────┴─────────┘")
    
    # Execution history
    print("\n📜 Recent Executions:")
    
    print("\n  ┌────────────────────────────────┬──────────┬──────────┬──────────┐")
    print("  │ Hook                           │ Status   │ Duration │ Exit     │")
    print("  ├────────────────────────────────┼──────────┼──────────┼──────────┤")
    
    for execution in platform.executions[-10:]:
        hook = platform.hooks.get(execution.hook_id)
        name = (hook.name if hook else "unknown")[:30].ljust(30)
        
        status_icons = {
            HookStatus.SUCCESS: "🟢",
            HookStatus.FAILED: "🔴",
            HookStatus.RUNNING: "🔵",
            HookStatus.PENDING: "⚪",
            HookStatus.TIMEOUT: "⏰",
            HookStatus.SKIPPED: "⏭️"
        }
        status = status_icons.get(execution.status, "⚪")[:8].ljust(8)
        duration = f"{execution.duration_ms}ms"[:8].ljust(8)
        exit_code = str(execution.exit_code)[:8].ljust(8)
        
        print(f"  │ {name} │ {status} │ {duration} │ {exit_code} │")
        
    print("  └────────────────────────────────┴──────────┴──────────┴──────────┘")
    
    # Hook type distribution
    print("\n📊 Hooks by Type:")
    
    stats = platform.get_statistics()
    
    type_icons = {
        "pre_deploy": "⬅️",
        "post_deploy": "➡️",
        "health_check": "💓",
        "notification": "📢",
        "custom": "🔧"
    }
    
    for htype, count in stats['hooks_by_type'].items():
        icon = type_icons.get(htype, "🪝")
        bar = "█" * (count * 2) + "░" * (10 - count * 2)
        print(f"  {icon} {htype:14s} [{bar}] {count}")
        
    # Execution statistics
    print("\n📈 Execution Statistics:")
    
    print(f"\n  Total Executions: {stats['total_executions']}")
    print(f"  Successful: {stats['successful_executions']}")
    print(f"  Failed: {stats['failed_executions']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Avg Duration: {stats['avg_duration_ms']:.0f}ms")
    
    # Script types
    print("\n📜 Script Types:")
    
    script_types = {}
    for script in platform.scripts.values():
        t = script.script_type
        script_types[t] = script_types.get(t, 0) + 1
        
    script_icons = {"bash": "🐚", "python": "🐍", "webhook": "🔗", "powershell": "💠"}
    for stype, count in script_types.items():
        icon = script_icons.get(stype, "📜")
        bar = "█" * (count * 2) + "░" * (10 - count * 2)
        print(f"  {icon} {stype:12s} [{bar}] {count}")
        
    # Deployment summary
    print("\n🚀 Deployment Summary:")
    
    for deployment in deployments:
        status_icon = "✅" if deployment.status == "success" else "❌"
        pre_icon = "✅" if deployment.pre_hooks_completed else "❌"
        post_icon = "✅" if deployment.post_hooks_completed else "❌"
        
        print(f"  {status_icon} {deployment.service} {deployment.version}")
        print(f"     Pre-hooks: {pre_icon}  Post-hooks: {post_icon}")
        
    # Statistics
    print("\n📊 Platform Statistics:")
    
    print(f"\n  Scripts: {stats['total_scripts']}")
    print(f"  Hooks: {stats['total_hooks']}")
    print(f"  Chains: {stats['total_chains']}")
    print(f"  Templates: {len(platform.templates)}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Deployment Hooks Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Hooks:                   {stats['total_hooks']:>12}                        │")
    print(f"│ Total Scripts:                 {stats['total_scripts']:>12}                        │")
    print(f"│ Total Executions:              {stats['total_executions']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                     {stats['success_rate']:>7.1f}%                       │")
    print(f"│ Avg Duration (ms):               {stats['avg_duration_ms']:>8.0f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Deployment Hooks Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
