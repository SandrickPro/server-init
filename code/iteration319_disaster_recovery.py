#!/usr/bin/env python3
"""
Server Init - Iteration 319: Disaster Recovery Platform
Платформа аварийного восстановления

Функционал:
- DR Plans - планы аварийного восстановления
- Failover Automation - автоматическое переключение
- Replication - репликация данных
- Health Monitoring - мониторинг состояния
- RTO/RPO Management - управление RTO/RPO
- Testing & Drills - тестирование DR
- Runbook Automation - автоматизация runbook
- Compliance Reporting - отчетность по соответствию
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class SiteType(Enum):
    """Тип сайта"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class SiteStatus(Enum):
    """Статус сайта"""
    ACTIVE = "active"
    STANDBY = "standby"
    FAILOVER = "failover"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class ReplicationType(Enum):
    """Тип репликации"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    SEMI_SYNCHRONOUS = "semi_synchronous"


class ReplicationStatus(Enum):
    """Статус репликации"""
    ACTIVE = "active"
    PAUSED = "paused"
    LAGGING = "lagging"
    FAILED = "failed"


class FailoverType(Enum):
    """Тип переключения"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class FailoverStatus(Enum):
    """Статус переключения"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class TestType(Enum):
    """Тип теста DR"""
    TABLETOP = "tabletop"
    WALKTHROUGH = "walkthrough"
    SIMULATION = "simulation"
    PARALLEL = "parallel"
    FULL_FAILOVER = "full_failover"


class ComponentType(Enum):
    """Тип компонента"""
    DATABASE = "database"
    APPLICATION = "application"
    STORAGE = "storage"
    NETWORK = "network"
    DNS = "dns"
    LOAD_BALANCER = "load_balancer"


@dataclass
class Site:
    """Сайт DR"""
    site_id: str
    name: str
    
    # Type
    site_type: SiteType = SiteType.PRIMARY
    
    # Status
    status: SiteStatus = SiteStatus.ACTIVE
    
    # Location
    location: str = ""
    region: str = ""
    
    # Infrastructure
    data_center: str = ""
    availability_zone: str = ""
    
    # Capacity
    total_capacity_tb: float = 0
    used_capacity_tb: float = 0
    
    # Network
    ip_range: str = ""
    vpn_endpoint: str = ""
    
    # Health
    health_score: int = 100
    last_health_check: Optional[datetime] = None


@dataclass
class Component:
    """Компонент для DR"""
    component_id: str
    name: str
    
    # Type
    component_type: ComponentType = ComponentType.APPLICATION
    
    # Site
    primary_site_id: str = ""
    secondary_site_id: str = ""
    
    # Criticality
    is_critical: bool = True
    priority: int = 1  # 1 = highest
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # component_ids
    
    # Health
    is_healthy: bool = True


@dataclass
class ReplicationPair:
    """Пара репликации"""
    pair_id: str
    name: str
    
    # Components
    source_component_id: str = ""
    target_component_id: str = ""
    
    # Source/Target sites
    source_site_id: str = ""
    target_site_id: str = ""
    
    # Type
    replication_type: ReplicationType = ReplicationType.ASYNCHRONOUS
    
    # Status
    status: ReplicationStatus = ReplicationStatus.ACTIVE
    
    # Lag
    lag_seconds: int = 0
    max_acceptable_lag_seconds: int = 300
    
    # Transfer
    bytes_replicated: int = 0
    last_sync: Optional[datetime] = None


@dataclass
class DRPlan:
    """План аварийного восстановления"""
    plan_id: str
    name: str
    
    # Sites
    primary_site_id: str = ""
    secondary_site_id: str = ""
    
    # Components
    component_ids: List[str] = field(default_factory=list)
    
    # RTO/RPO
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective
    
    # Failover type
    failover_type: FailoverType = FailoverType.MANUAL
    
    # Thresholds
    auto_failover_threshold: int = 3  # consecutive failures
    
    # Status
    is_active: bool = True
    
    # Steps
    failover_steps: List[Dict[str, Any]] = field(default_factory=list)
    failback_steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Last test
    last_test_date: Optional[datetime] = None
    last_test_result: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class FailoverEvent:
    """Событие переключения"""
    event_id: str
    plan_id: str
    
    # Type
    failover_type: FailoverType = FailoverType.MANUAL
    is_failback: bool = False
    
    # Status
    status: FailoverStatus = FailoverStatus.NOT_STARTED
    
    # Sites
    from_site_id: str = ""
    to_site_id: str = ""
    
    # Progress
    current_step: int = 0
    total_steps: int = 0
    progress_percent: float = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    # Metrics
    rto_achieved_minutes: float = 0
    rpo_achieved_minutes: float = 0
    
    # Issues
    errors: List[str] = field(default_factory=list)
    
    # Triggered by
    triggered_by: str = ""
    trigger_reason: str = ""


@dataclass
class DRTest:
    """Тест DR"""
    test_id: str
    plan_id: str
    
    # Type
    test_type: TestType = TestType.SIMULATION
    
    # Status
    is_passed: bool = False
    is_completed: bool = False
    
    # Timing
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    rto_achieved_minutes: float = 0
    rpo_achieved_minutes: float = 0
    
    # Findings
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Participants
    participants: List[str] = field(default_factory=list)


@dataclass
class RunbookStep:
    """Шаг runbook"""
    step_id: str
    runbook_id: str
    
    # Order
    order: int = 0
    
    # Description
    name: str = ""
    description: str = ""
    
    # Type
    is_automated: bool = True
    
    # Command/Script
    command: str = ""
    script_path: str = ""
    
    # Expected duration
    expected_duration_seconds: int = 60
    
    # Validation
    validation_command: str = ""
    expected_output: str = ""
    
    # Rollback
    rollback_command: str = ""


class DisasterRecoveryManager:
    """Менеджер аварийного восстановления"""
    
    def __init__(self):
        self.sites: Dict[str, Site] = {}
        self.components: Dict[str, Component] = {}
        self.replication_pairs: Dict[str, ReplicationPair] = {}
        self.dr_plans: Dict[str, DRPlan] = {}
        self.failover_events: List[FailoverEvent] = []
        self.dr_tests: List[DRTest] = []
        self.runbook_steps: Dict[str, List[RunbookStep]] = {}
        
    async def create_site(self, name: str,
                         site_type: SiteType,
                         location: str,
                         region: str,
                         capacity_tb: float = 100) -> Site:
        """Создание сайта"""
        site = Site(
            site_id=f"site_{uuid.uuid4().hex[:8]}",
            name=name,
            site_type=site_type,
            location=location,
            region=region,
            total_capacity_tb=capacity_tb,
            status=SiteStatus.ACTIVE if site_type == SiteType.PRIMARY else SiteStatus.STANDBY
        )
        
        self.sites[site.site_id] = site
        return site
        
    async def create_component(self, name: str,
                              component_type: ComponentType,
                              primary_site_id: str,
                              secondary_site_id: str,
                              is_critical: bool = True,
                              priority: int = 1,
                              depends_on: List[str] = None) -> Component:
        """Создание компонента"""
        component = Component(
            component_id=f"comp_{uuid.uuid4().hex[:8]}",
            name=name,
            component_type=component_type,
            primary_site_id=primary_site_id,
            secondary_site_id=secondary_site_id,
            is_critical=is_critical,
            priority=priority,
            depends_on=depends_on or []
        )
        
        self.components[component.component_id] = component
        return component
        
    async def create_replication_pair(self, name: str,
                                     source_component_id: str,
                                     target_component_id: str,
                                     replication_type: ReplicationType = ReplicationType.ASYNCHRONOUS,
                                     max_lag_seconds: int = 300) -> ReplicationPair:
        """Создание пары репликации"""
        source = self.components.get(source_component_id)
        target = self.components.get(target_component_id)
        
        pair = ReplicationPair(
            pair_id=f"repl_{uuid.uuid4().hex[:8]}",
            name=name,
            source_component_id=source_component_id,
            target_component_id=target_component_id,
            source_site_id=source.primary_site_id if source else "",
            target_site_id=target.secondary_site_id if target else "",
            replication_type=replication_type,
            max_acceptable_lag_seconds=max_lag_seconds,
            last_sync=datetime.now()
        )
        
        self.replication_pairs[pair.pair_id] = pair
        return pair
        
    async def create_dr_plan(self, name: str,
                            primary_site_id: str,
                            secondary_site_id: str,
                            component_ids: List[str],
                            rto_minutes: int = 60,
                            rpo_minutes: int = 15,
                            failover_type: FailoverType = FailoverType.MANUAL) -> DRPlan:
        """Создание плана DR"""
        plan = DRPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            primary_site_id=primary_site_id,
            secondary_site_id=secondary_site_id,
            component_ids=component_ids,
            rto_minutes=rto_minutes,
            rpo_minutes=rpo_minutes,
            failover_type=failover_type
        )
        
        # Generate default failover steps
        plan.failover_steps = [
            {"order": 1, "name": "Verify site health", "type": "check"},
            {"order": 2, "name": "Stop primary services", "type": "action"},
            {"order": 3, "name": "Activate secondary database", "type": "action"},
            {"order": 4, "name": "Update DNS records", "type": "action"},
            {"order": 5, "name": "Start secondary services", "type": "action"},
            {"order": 6, "name": "Verify failover", "type": "check"}
        ]
        
        plan.failback_steps = [
            {"order": 1, "name": "Sync data to primary", "type": "action"},
            {"order": 2, "name": "Verify data consistency", "type": "check"},
            {"order": 3, "name": "Switch traffic to primary", "type": "action"},
            {"order": 4, "name": "Verify failback", "type": "check"}
        ]
        
        self.dr_plans[plan.plan_id] = plan
        return plan
        
    async def execute_failover(self, plan_id: str,
                              triggered_by: str = "manual",
                              reason: str = "") -> Optional[FailoverEvent]:
        """Выполнение переключения"""
        plan = self.dr_plans.get(plan_id)
        if not plan:
            return None
            
        event = FailoverEvent(
            event_id=f"fo_{uuid.uuid4().hex[:8]}",
            plan_id=plan_id,
            failover_type=plan.failover_type,
            from_site_id=plan.primary_site_id,
            to_site_id=plan.secondary_site_id,
            total_steps=len(plan.failover_steps),
            triggered_by=triggered_by,
            trigger_reason=reason,
            started_at=datetime.now()
        )
        
        event.status = FailoverStatus.IN_PROGRESS
        
        # Execute steps
        for i, step in enumerate(plan.failover_steps):
            event.current_step = i + 1
            event.progress_percent = (i + 1) / event.total_steps * 100
            
            # Simulate step execution
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            # Random failure chance
            if random.random() < 0.02:  # 2% failure chance per step
                event.errors.append(f"Step {i + 1}: {step['name']} failed")
                
        if event.errors:
            event.status = FailoverStatus.FAILED
        else:
            event.status = FailoverStatus.COMPLETED
            
            # Update site statuses
            primary = self.sites.get(plan.primary_site_id)
            secondary = self.sites.get(plan.secondary_site_id)
            
            if primary:
                primary.status = SiteStatus.STANDBY
            if secondary:
                secondary.status = SiteStatus.ACTIVE
                
        event.completed_at = datetime.now()
        event.duration_seconds = (event.completed_at - event.started_at).total_seconds()
        event.rto_achieved_minutes = event.duration_seconds / 60
        
        # Calculate RPO from replication lag
        max_lag = 0
        for pair in self.replication_pairs.values():
            if pair.source_site_id == plan.primary_site_id:
                max_lag = max(max_lag, pair.lag_seconds)
        event.rpo_achieved_minutes = max_lag / 60
        
        self.failover_events.append(event)
        return event
        
    async def execute_failback(self, plan_id: str) -> Optional[FailoverEvent]:
        """Выполнение обратного переключения"""
        plan = self.dr_plans.get(plan_id)
        if not plan:
            return None
            
        event = FailoverEvent(
            event_id=f"fb_{uuid.uuid4().hex[:8]}",
            plan_id=plan_id,
            failover_type=FailoverType.MANUAL,
            is_failback=True,
            from_site_id=plan.secondary_site_id,
            to_site_id=plan.primary_site_id,
            total_steps=len(plan.failback_steps),
            triggered_by="manual",
            trigger_reason="Planned failback",
            started_at=datetime.now()
        )
        
        event.status = FailoverStatus.IN_PROGRESS
        
        # Execute steps
        for i, step in enumerate(plan.failback_steps):
            event.current_step = i + 1
            event.progress_percent = (i + 1) / event.total_steps * 100
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
        event.status = FailoverStatus.COMPLETED
        event.completed_at = datetime.now()
        event.duration_seconds = (event.completed_at - event.started_at).total_seconds()
        event.rto_achieved_minutes = event.duration_seconds / 60
        
        # Update site statuses
        primary = self.sites.get(plan.primary_site_id)
        secondary = self.sites.get(plan.secondary_site_id)
        
        if primary:
            primary.status = SiteStatus.ACTIVE
        if secondary:
            secondary.status = SiteStatus.STANDBY
            
        self.failover_events.append(event)
        return event
        
    async def schedule_dr_test(self, plan_id: str,
                              test_type: TestType,
                              scheduled_at: datetime = None,
                              participants: List[str] = None) -> Optional[DRTest]:
        """Планирование теста DR"""
        plan = self.dr_plans.get(plan_id)
        if not plan:
            return None
            
        test = DRTest(
            test_id=f"test_{uuid.uuid4().hex[:8]}",
            plan_id=plan_id,
            test_type=test_type,
            scheduled_at=scheduled_at or datetime.now(),
            participants=participants or []
        )
        
        self.dr_tests.append(test)
        return test
        
    async def execute_dr_test(self, test_id: str) -> bool:
        """Выполнение теста DR"""
        test = next((t for t in self.dr_tests if t.test_id == test_id), None)
        if not test:
            return False
            
        plan = self.dr_plans.get(test.plan_id)
        if not plan:
            return False
            
        test.started_at = datetime.now()
        
        # Simulate test based on type
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Simulate results
        test.rto_achieved_minutes = plan.rto_minutes * random.uniform(0.5, 1.2)
        test.rpo_achieved_minutes = plan.rpo_minutes * random.uniform(0.5, 1.5)
        
        # Check if passed
        rto_ok = test.rto_achieved_minutes <= plan.rto_minutes
        rpo_ok = test.rpo_achieved_minutes <= plan.rpo_minutes
        
        test.is_passed = rto_ok and rpo_ok
        test.is_completed = True
        test.completed_at = datetime.now()
        
        # Generate findings
        if not rto_ok:
            test.issues_found.append(f"RTO exceeded: {test.rto_achieved_minutes:.1f}min vs target {plan.rto_minutes}min")
            test.recommendations.append("Optimize failover automation scripts")
            
        if not rpo_ok:
            test.issues_found.append(f"RPO exceeded: {test.rpo_achieved_minutes:.1f}min vs target {plan.rpo_minutes}min")
            test.recommendations.append("Increase replication frequency")
            
        if random.random() < 0.3:
            test.issues_found.append("Documentation needs updating")
            test.recommendations.append("Review and update runbooks")
            
        # Update plan
        plan.last_test_date = datetime.now()
        plan.last_test_result = "PASSED" if test.is_passed else "FAILED"
        
        return test.is_passed
        
    async def update_replication_status(self):
        """Обновление статуса репликации"""
        for pair in self.replication_pairs.values():
            # Simulate lag
            if pair.replication_type == ReplicationType.SYNCHRONOUS:
                pair.lag_seconds = random.randint(0, 5)
            elif pair.replication_type == ReplicationType.SEMI_SYNCHRONOUS:
                pair.lag_seconds = random.randint(0, 30)
            else:
                pair.lag_seconds = random.randint(0, 300)
                
            # Update status based on lag
            if pair.lag_seconds > pair.max_acceptable_lag_seconds:
                pair.status = ReplicationStatus.LAGGING
            else:
                pair.status = ReplicationStatus.ACTIVE
                
            pair.bytes_replicated += random.randint(1000000, 10000000)
            pair.last_sync = datetime.now()
            
    async def health_check(self):
        """Проверка здоровья"""
        for site in self.sites.values():
            # Simulate health score
            base_score = 100
            
            # Check components in site
            for component in self.components.values():
                if component.primary_site_id == site.site_id:
                    if not component.is_healthy:
                        base_score -= 10
                        
            # Check replication pairs
            for pair in self.replication_pairs.values():
                if pair.source_site_id == site.site_id:
                    if pair.status != ReplicationStatus.ACTIVE:
                        base_score -= 15
                        
            site.health_score = max(0, base_score)
            site.last_health_check = datetime.now()
            
    def get_rto_rpo_status(self) -> Dict[str, Any]:
        """Статус RTO/RPO"""
        results = {}
        
        for plan in self.dr_plans.values():
            # Get actual RPO from replication
            actual_rpo_seconds = 0
            for pair in self.replication_pairs.values():
                if pair.source_site_id == plan.primary_site_id:
                    actual_rpo_seconds = max(actual_rpo_seconds, pair.lag_seconds)
                    
            # Estimate RTO from last test or events
            last_test = next((t for t in reversed(self.dr_tests) 
                            if t.plan_id == plan.plan_id and t.is_completed), None)
            actual_rto = last_test.rto_achieved_minutes if last_test else plan.rto_minutes
            
            results[plan.plan_id] = {
                "plan_name": plan.name,
                "target_rto_minutes": plan.rto_minutes,
                "target_rpo_minutes": plan.rpo_minutes,
                "actual_rto_minutes": actual_rto,
                "actual_rpo_minutes": actual_rpo_seconds / 60,
                "rto_status": "OK" if actual_rto <= plan.rto_minutes else "WARNING",
                "rpo_status": "OK" if actual_rpo_seconds / 60 <= plan.rpo_minutes else "WARNING"
            }
            
        return results
        
    def get_compliance_report(self) -> Dict[str, Any]:
        """Отчет о соответствии"""
        total_plans = len(self.dr_plans)
        
        tested_recently = sum(1 for p in self.dr_plans.values() 
                             if p.last_test_date and 
                             p.last_test_date > datetime.now() - timedelta(days=90))
        
        passed_last_test = sum(1 for p in self.dr_plans.values() 
                              if p.last_test_result == "PASSED")
        
        rto_rpo = self.get_rto_rpo_status()
        rto_ok = sum(1 for r in rto_rpo.values() if r["rto_status"] == "OK")
        rpo_ok = sum(1 for r in rto_rpo.values() if r["rpo_status"] == "OK")
        
        repl_healthy = sum(1 for p in self.replication_pairs.values() 
                         if p.status == ReplicationStatus.ACTIVE)
        
        return {
            "total_dr_plans": total_plans,
            "tested_within_90_days": tested_recently,
            "testing_compliance": (tested_recently / total_plans * 100) if total_plans > 0 else 0,
            "passed_last_test": passed_last_test,
            "rto_compliant": rto_ok,
            "rpo_compliant": rpo_ok,
            "replication_healthy": repl_healthy,
            "total_replication_pairs": len(self.replication_pairs),
            "overall_compliance_score": self._calculate_compliance_score()
        }
        
    def _calculate_compliance_score(self) -> float:
        """Расчет общего балла соответствия"""
        score = 100
        
        # Testing compliance
        for plan in self.dr_plans.values():
            if not plan.last_test_date:
                score -= 10
            elif plan.last_test_date < datetime.now() - timedelta(days=90):
                score -= 5
                
        # Replication health
        for pair in self.replication_pairs.values():
            if pair.status != ReplicationStatus.ACTIVE:
                score -= 5
                
        return max(0, score)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_sites = len(self.sites)
        primary_sites = sum(1 for s in self.sites.values() if s.site_type == SiteType.PRIMARY)
        
        by_site_status = {}
        for s in self.sites.values():
            by_site_status[s.status.value] = by_site_status.get(s.status.value, 0) + 1
            
        total_components = len(self.components)
        critical_components = sum(1 for c in self.components.values() if c.is_critical)
        
        total_failovers = len(self.failover_events)
        successful_failovers = sum(1 for f in self.failover_events 
                                   if f.status == FailoverStatus.COMPLETED)
        
        total_tests = len(self.dr_tests)
        passed_tests = sum(1 for t in self.dr_tests if t.is_passed)
        
        avg_rto = sum(f.rto_achieved_minutes for f in self.failover_events) / total_failovers if total_failovers > 0 else 0
        avg_rpo = sum(f.rpo_achieved_minutes for f in self.failover_events) / total_failovers if total_failovers > 0 else 0
        
        return {
            "total_sites": total_sites,
            "primary_sites": primary_sites,
            "by_site_status": by_site_status,
            "total_components": total_components,
            "critical_components": critical_components,
            "total_dr_plans": len(self.dr_plans),
            "active_dr_plans": sum(1 for p in self.dr_plans.values() if p.is_active),
            "total_replication_pairs": len(self.replication_pairs),
            "healthy_replication": sum(1 for p in self.replication_pairs.values() 
                                       if p.status == ReplicationStatus.ACTIVE),
            "total_failovers": total_failovers,
            "successful_failovers": successful_failovers,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "avg_rto_minutes": avg_rto,
            "avg_rpo_minutes": avg_rpo
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 319: Disaster Recovery Platform")
    print("=" * 60)
    
    dr = DisasterRecoveryManager()
    print("✓ Disaster Recovery Manager created")
    
    # Create sites
    print("\n🏢 Creating DR Sites...")
    
    sites_data = [
        ("Primary DC East", SiteType.PRIMARY, "New York", "us-east-1", 500),
        ("Secondary DC West", SiteType.SECONDARY, "Los Angeles", "us-west-2", 500),
        ("Tertiary DC EU", SiteType.TERTIARY, "Frankfurt", "eu-central-1", 300)
    ]
    
    sites = []
    for name, s_type, location, region, capacity in sites_data:
        site = await dr.create_site(name, s_type, location, region, capacity)
        sites.append(site)
        print(f"  🏢 {name} ({s_type.value}) - {location}")
        
    # Create components
    print("\n📦 Creating DR Components...")
    
    components_data = [
        ("Production Database", ComponentType.DATABASE, True, 1, []),
        ("Application Server", ComponentType.APPLICATION, True, 2, ["comp_database"]),
        ("File Storage", ComponentType.STORAGE, True, 2, []),
        ("Load Balancer", ComponentType.LOAD_BALANCER, True, 1, []),
        ("DNS Service", ComponentType.DNS, True, 1, []),
        ("Cache Server", ComponentType.APPLICATION, False, 3, []),
        ("Queue Service", ComponentType.APPLICATION, True, 2, ["comp_database"]),
        ("API Gateway", ComponentType.APPLICATION, True, 1, ["comp_lb"])
    ]
    
    components = []
    for name, c_type, critical, priority, deps in components_data:
        component = await dr.create_component(
            name, c_type, sites[0].site_id, sites[1].site_id, 
            critical, priority, deps
        )
        components.append(component)
        crit_str = "🔴" if critical else "⚪"
        print(f"  {crit_str} {name} ({c_type.value}) P{priority}")
        
    # Create replication pairs
    print("\n🔄 Creating Replication Pairs...")
    
    repl_data = [
        ("Database Replication", components[0], ReplicationType.SYNCHRONOUS, 5),
        ("File Storage Sync", components[2], ReplicationType.ASYNCHRONOUS, 300),
        ("Queue Replication", components[6], ReplicationType.SEMI_SYNCHRONOUS, 30)
    ]
    
    repl_pairs = []
    for name, comp, repl_type, max_lag in repl_data:
        pair = await dr.create_replication_pair(name, comp.component_id, comp.component_id, repl_type, max_lag)
        repl_pairs.append(pair)
        print(f"  🔄 {name} ({repl_type.value})")
        
    # Update replication status
    await dr.update_replication_status()
    
    # Create DR plans
    print("\n📋 Creating DR Plans...")
    
    plans_data = [
        ("Full Site Failover", [c.component_id for c in components[:5]], 60, 15, FailoverType.AUTOMATIC),
        ("Database Only", [components[0].component_id], 15, 5, FailoverType.MANUAL),
        ("Application Tier", [c.component_id for c in components[1:4]], 30, 10, FailoverType.MANUAL)
    ]
    
    plans = []
    for name, comp_ids, rto, rpo, fo_type in plans_data:
        plan = await dr.create_dr_plan(
            name, sites[0].site_id, sites[1].site_id, 
            comp_ids, rto, rpo, fo_type
        )
        plans.append(plan)
        print(f"  📋 {name} (RTO: {rto}min, RPO: {rpo}min)")
        
    # Run health check
    await dr.health_check()
    
    # Schedule and run DR tests
    print("\n🧪 Running DR Tests...")
    
    for plan in plans:
        test = await dr.schedule_dr_test(
            plan.plan_id, 
            TestType.SIMULATION,
            participants=["DR Team", "Operations"]
        )
        
        if test:
            passed = await dr.execute_dr_test(test.test_id)
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"  {status} {plan.name}")
            print(f"    RTO: {test.rto_achieved_minutes:.1f}min (target: {plan.rto_minutes}min)")
            print(f"    RPO: {test.rpo_achieved_minutes:.1f}min (target: {plan.rpo_minutes}min)")
            
    # Execute failover
    print("\n⚡ Executing Failover...")
    
    failover = await dr.execute_failover(
        plans[1].plan_id,  # Database only
        triggered_by="automation",
        reason="Primary database unresponsive"
    )
    
    if failover:
        status = "✓" if failover.status == FailoverStatus.COMPLETED else "✗"
        print(f"  [{status}] {plans[1].name}")
        print(f"    Duration: {failover.duration_seconds:.1f}s")
        print(f"    RTO achieved: {failover.rto_achieved_minutes:.1f}min")
        
    # Execute failback
    print("\n🔙 Executing Failback...")
    
    failback = await dr.execute_failback(plans[1].plan_id)
    
    if failback:
        status = "✓" if failback.status == FailoverStatus.COMPLETED else "✗"
        print(f"  [{status}] Failback completed in {failback.duration_seconds:.1f}s")
        
    # Site status
    print("\n🏢 Site Status:")
    
    print("\n  ┌───────────────────────────┬─────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ Site                      │ Type        │ Status       │ Health       │ Location     │")
    print("  ├───────────────────────────┼─────────────┼──────────────┼──────────────┼──────────────┤")
    
    for site in sites:
        name = site.name[:25].ljust(25)
        s_type = site.site_type.value[:11].ljust(11)
        status = site.status.value[:12].ljust(12)
        health = f"{site.health_score}%".ljust(12)
        location = site.location[:12].ljust(12)
        
        print(f"  │ {name} │ {s_type} │ {status} │ {health} │ {location} │")
        
    print("  └───────────────────────────┴─────────────┴──────────────┴──────────────┴──────────────┘")
    
    # Replication status
    print("\n🔄 Replication Status:")
    
    print("\n  ┌───────────────────────────┬─────────────────────┬───────────────┬───────────┬────────────────┐")
    print("  │ Pair                      │ Type                │ Status        │ Lag       │ Last Sync      │")
    print("  ├───────────────────────────┼─────────────────────┼───────────────┼───────────┼────────────────┤")
    
    for pair in repl_pairs:
        name = pair.name[:25].ljust(25)
        r_type = pair.replication_type.value[:19].ljust(19)
        status = pair.status.value[:13].ljust(13)
        lag = f"{pair.lag_seconds}s"[:9].ljust(9)
        sync = pair.last_sync.strftime("%H:%M:%S") if pair.last_sync else "N/A"
        sync = sync[:14].ljust(14)
        
        print(f"  │ {name} │ {r_type} │ {status} │ {lag} │ {sync} │")
        
    print("  └───────────────────────────┴─────────────────────┴───────────────┴───────────┴────────────────┘")
    
    # DR Plans
    print("\n📋 DR Plans:")
    
    for plan in plans:
        status = "✓ Active" if plan.is_active else "✗ Inactive"
        test_result = plan.last_test_result or "Not tested"
        test_date = plan.last_test_date.strftime("%Y-%m-%d") if plan.last_test_date else "N/A"
        
        print(f"\n  📋 {plan.name}")
        print(f"     Status: {status}")
        print(f"     RTO: {plan.rto_minutes} min | RPO: {plan.rpo_minutes} min")
        print(f"     Failover Type: {plan.failover_type.value}")
        print(f"     Components: {len(plan.component_ids)}")
        print(f"     Last Test: {test_date} ({test_result})")
        
    # RTO/RPO Status
    print("\n⏱️ RTO/RPO Status:")
    
    rto_rpo = dr.get_rto_rpo_status()
    
    print("\n  ┌───────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐")
    print("  │ Plan                      │ RTO (Target/Actual)             │ RPO (Target/Actual)             │")
    print("  ├───────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤")
    
    for plan_id, info in rto_rpo.items():
        name = info['plan_name'][:25].ljust(25)
        
        rto_status = "✓" if info['rto_status'] == "OK" else "⚠"
        rto = f"{rto_status} {info['target_rto_minutes']}min / {info['actual_rto_minutes']:.1f}min"[:31].ljust(31)
        
        rpo_status = "✓" if info['rpo_status'] == "OK" else "⚠"
        rpo = f"{rpo_status} {info['target_rpo_minutes']}min / {info['actual_rpo_minutes']:.1f}min"[:31].ljust(31)
        
        print(f"  │ {name} │ {rto} │ {rpo} │")
        
    print("  └───────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘")
    
    # Component status
    print("\n📦 Component Status:")
    
    by_priority = {}
    for comp in components:
        by_priority.setdefault(comp.priority, []).append(comp)
        
    for priority in sorted(by_priority.keys()):
        print(f"\n  Priority {priority}:")
        for comp in by_priority[priority]:
            health = "✓" if comp.is_healthy else "✗"
            crit = "🔴 Critical" if comp.is_critical else "⚪ Standard"
            print(f"    [{health}] {comp.name} ({comp.component_type.value}) - {crit}")
            
    # Failover history
    print("\n📊 Failover History:")
    
    if dr.failover_events:
        print("\n  ┌─────────────────────────┬─────────────┬───────────────┬───────────────┬──────────────────────────┐")
        print("  │ Event                   │ Type        │ Status        │ Duration      │ Reason                   │")
        print("  ├─────────────────────────┼─────────────┼───────────────┼───────────────┼──────────────────────────┤")
        
        for event in dr.failover_events[-5:]:
            plan = dr.dr_plans.get(event.plan_id)
            name = (plan.name if plan else "Unknown")[:23].ljust(23)
            e_type = ("Failback" if event.is_failback else "Failover")[:11].ljust(11)
            status = event.status.value[:13].ljust(13)
            duration = f"{event.duration_seconds:.1f}s"[:13].ljust(13)
            reason = event.trigger_reason[:24].ljust(24)
            
            print(f"  │ {name} │ {e_type} │ {status} │ {duration} │ {reason} │")
            
        print("  └─────────────────────────┴─────────────┴───────────────┴───────────────┴──────────────────────────┘")
    else:
        print("  No failover events recorded")
        
    # Compliance report
    print("\n📋 Compliance Report:")
    
    compliance = dr.get_compliance_report()
    
    print(f"\n  DR Plans: {compliance['total_dr_plans']}")
    print(f"  Tested (90 days): {compliance['tested_within_90_days']} ({compliance['testing_compliance']:.0f}%)")
    print(f"  Passed Last Test: {compliance['passed_last_test']}")
    print(f"  RTO Compliant: {compliance['rto_compliant']}")
    print(f"  RPO Compliant: {compliance['rpo_compliant']}")
    print(f"  Replication Healthy: {compliance['replication_healthy']}/{compliance['total_replication_pairs']}")
    print(f"\n  Overall Compliance Score: {compliance['overall_compliance_score']:.0f}%")
    
    # Statistics
    print("\n📊 DR Statistics:")
    
    stats = dr.get_statistics()
    
    print(f"\n  Total Sites: {stats['total_sites']}")
    print(f"  Primary Sites: {stats['primary_sites']}")
    print("  By Status:")
    for status, count in stats['by_site_status'].items():
        print(f"    {status}: {count}")
        
    print(f"\n  Total Components: {stats['total_components']}")
    print(f"  Critical Components: {stats['critical_components']}")
    
    print(f"\n  DR Plans: {stats['total_dr_plans']} ({stats['active_dr_plans']} active)")
    print(f"  Replication Pairs: {stats['healthy_replication']}/{stats['total_replication_pairs']} healthy")
    
    print(f"\n  Failover Events: {stats['total_failovers']}")
    print(f"  Successful: {stats['successful_failovers']}")
    
    print(f"\n  DR Tests: {stats['total_tests']}")
    print(f"  Passed: {stats['passed_tests']}")
    
    print(f"\n  Avg RTO Achieved: {stats['avg_rto_minutes']:.1f} min")
    print(f"  Avg RPO Achieved: {stats['avg_rpo_minutes']:.1f} min")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Disaster Recovery Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Sites:                 {stats['total_sites']:>12}                          │")
    print(f"│ Critical Components:         {stats['critical_components']:>12}                          │")
    print(f"│ Active DR Plans:             {stats['active_dr_plans']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliance Score:            {compliance['overall_compliance_score']:>11.0f}%                          │")
    print(f"│ Replication Health:          {stats['healthy_replication']}/{stats['total_replication_pairs']:>8} healthy                    │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Disaster Recovery Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
