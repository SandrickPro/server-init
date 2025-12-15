#!/usr/bin/env python3
"""
Server Init - Iteration 305: Problem Management Platform
Платформа управления проблемами (ITIL Problem Management)

Функционал:
- Problem Detection - обнаружение проблем
- Root Cause Analysis - анализ первопричин
- Known Error Database - база известных ошибок
- Workaround Management - управление обходными решениями
- Problem Resolution - решение проблем
- Trend Analysis - анализ трендов
- Prevention Planning - планирование предотвращения
- Knowledge Integration - интеграция со знаниями
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class ProblemStatus(Enum):
    """Статус проблемы"""
    NEW = "new"
    OPEN = "open"
    INVESTIGATING = "investigating"
    ROOT_CAUSE_IDENTIFIED = "root_cause_identified"
    KNOWN_ERROR = "known_error"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ProblemPriority(Enum):
    """Приоритет проблемы"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProblemCategory(Enum):
    """Категория проблемы"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    CAPACITY = "capacity"
    INTEGRATION = "integration"


class RCAMethod(Enum):
    """Метод анализа первопричин"""
    FIVE_WHYS = "five_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    PARETO = "pareto"
    TIMELINE = "timeline"


@dataclass
class RelatedIncident:
    """Связанный инцидент"""
    incident_id: str
    title: str
    severity: str
    occurred_at: datetime
    
    # Impact
    affected_users: int = 0
    duration_minutes: int = 0


@dataclass
class RootCauseAnalysis:
    """Анализ первопричин"""
    rca_id: str
    problem_id: str
    
    # Method
    method: RCAMethod = RCAMethod.FIVE_WHYS
    
    # Analysis
    root_cause: str = ""
    contributing_factors: List[str] = field(default_factory=list)
    
    # Evidence
    evidence: List[str] = field(default_factory=list)
    logs_analyzed: List[str] = field(default_factory=list)
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # Conclusions
    conclusions: str = ""
    
    # Status
    status: str = "in_progress"  # in_progress, completed, reviewed
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Workaround:
    """Обходное решение"""
    workaround_id: str
    problem_id: str
    
    # Details
    title: str = ""
    description: str = ""
    steps: List[str] = field(default_factory=list)
    
    # Effectiveness
    effectiveness: float = 0.0  # 0-100%
    risk_level: str = "low"  # low, medium, high
    
    # Usage
    usage_count: int = 0
    
    # Status
    is_temporary: bool = True
    is_approved: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnownError:
    """Известная ошибка"""
    ke_id: str
    problem_id: str
    
    # Details
    title: str = ""
    description: str = ""
    symptoms: List[str] = field(default_factory=list)
    
    # Root cause
    root_cause: str = ""
    
    # Workaround
    workaround_id: Optional[str] = None
    
    # Resolution
    resolution_status: str = "pending"  # pending, in_progress, planned, resolved
    planned_fix_version: str = ""
    fix_eta: Optional[datetime] = None
    
    # Knowledge
    kb_article_id: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Problem:
    """Проблема"""
    problem_id: str
    title: str
    description: str
    
    # Classification
    category: ProblemCategory = ProblemCategory.SOFTWARE
    priority: ProblemPriority = ProblemPriority.MEDIUM
    status: ProblemStatus = ProblemStatus.NEW
    
    # Related incidents
    related_incidents: List[str] = field(default_factory=list)
    
    # Impact
    impact_assessment: str = ""
    affected_services: List[str] = field(default_factory=list)
    affected_users: int = 0
    
    # Investigation
    assigned_to: str = ""
    team: str = ""
    
    # Analysis
    rca_id: Optional[str] = None
    root_cause: str = ""
    
    # Solutions
    workaround_ids: List[str] = field(default_factory=list)
    known_error_id: Optional[str] = None
    
    # Resolution
    resolution: str = ""
    permanent_fix: str = ""
    
    # Prevention
    prevention_actions: List[str] = field(default_factory=list)
    
    # Timestamps
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


@dataclass
class TrendPattern:
    """Паттерн тренда"""
    pattern_id: str
    
    # Pattern
    category: ProblemCategory
    description: str
    
    # Frequency
    occurrence_count: int = 0
    time_period_days: int = 30
    
    # Impact
    total_incidents: int = 0
    total_affected_users: int = 0
    
    # Recommendation
    recommendation: str = ""


class ProblemManagementManager:
    """Менеджер Problem Management"""
    
    def __init__(self):
        self.problems: Dict[str, Problem] = {}
        self.rcas: Dict[str, RootCauseAnalysis] = {}
        self.workarounds: Dict[str, Workaround] = {}
        self.known_errors: Dict[str, KnownError] = {}
        self.incidents: Dict[str, RelatedIncident] = {}
        self.trends: Dict[str, TrendPattern] = {}
        
    async def create_problem(self, title: str, description: str,
                            category: ProblemCategory,
                            priority: ProblemPriority = ProblemPriority.MEDIUM,
                            affected_services: List[str] = None) -> Problem:
        """Создание проблемы"""
        problem = Problem(
            problem_id=f"prb_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            category=category,
            priority=priority,
            affected_services=affected_services or []
        )
        
        self.problems[problem.problem_id] = problem
        return problem
        
    async def link_incident(self, problem_id: str,
                           incident_id: str,
                           title: str,
                           severity: str,
                           affected_users: int = 0,
                           duration_minutes: int = 0) -> bool:
        """Связывание инцидента с проблемой"""
        problem = self.problems.get(problem_id)
        if not problem:
            return False
            
        incident = RelatedIncident(
            incident_id=incident_id,
            title=title,
            severity=severity,
            occurred_at=datetime.now(),
            affected_users=affected_users,
            duration_minutes=duration_minutes
        )
        
        self.incidents[incident_id] = incident
        problem.related_incidents.append(incident_id)
        problem.affected_users += affected_users
        
        return True
        
    async def assign_problem(self, problem_id: str,
                            assigned_to: str,
                            team: str = "") -> bool:
        """Назначение проблемы"""
        problem = self.problems.get(problem_id)
        if not problem:
            return False
            
        problem.assigned_to = assigned_to
        problem.team = team
        problem.status = ProblemStatus.OPEN
        
        return True
        
    async def start_rca(self, problem_id: str,
                       method: RCAMethod = RCAMethod.FIVE_WHYS) -> Optional[RootCauseAnalysis]:
        """Начать анализ первопричин"""
        problem = self.problems.get(problem_id)
        if not problem:
            return None
            
        rca = RootCauseAnalysis(
            rca_id=f"rca_{uuid.uuid4().hex[:8]}",
            problem_id=problem_id,
            method=method
        )
        
        self.rcas[rca.rca_id] = rca
        problem.rca_id = rca.rca_id
        problem.status = ProblemStatus.INVESTIGATING
        
        return rca
        
    async def update_rca(self, rca_id: str,
                        root_cause: str = "",
                        contributing_factors: List[str] = None,
                        evidence: List[str] = None,
                        conclusions: str = "") -> bool:
        """Обновление RCA"""
        rca = self.rcas.get(rca_id)
        if not rca:
            return False
            
        if root_cause:
            rca.root_cause = root_cause
        if contributing_factors:
            rca.contributing_factors = contributing_factors
        if evidence:
            rca.evidence = evidence
        if conclusions:
            rca.conclusions = conclusions
            
        return True
        
    async def complete_rca(self, rca_id: str, root_cause: str) -> bool:
        """Завершение RCA"""
        rca = self.rcas.get(rca_id)
        if not rca:
            return False
            
        rca.root_cause = root_cause
        rca.status = "completed"
        rca.completed_at = datetime.now()
        
        # Update problem
        problem = self.problems.get(rca.problem_id)
        if problem:
            problem.root_cause = root_cause
            problem.status = ProblemStatus.ROOT_CAUSE_IDENTIFIED
            
        return True
        
    async def create_workaround(self, problem_id: str,
                               title: str,
                               description: str,
                               steps: List[str],
                               effectiveness: float = 80.0) -> Optional[Workaround]:
        """Создание обходного решения"""
        problem = self.problems.get(problem_id)
        if not problem:
            return None
            
        workaround = Workaround(
            workaround_id=f"wa_{uuid.uuid4().hex[:8]}",
            problem_id=problem_id,
            title=title,
            description=description,
            steps=steps,
            effectiveness=effectiveness
        )
        
        self.workarounds[workaround.workaround_id] = workaround
        problem.workaround_ids.append(workaround.workaround_id)
        
        return workaround
        
    async def approve_workaround(self, workaround_id: str) -> bool:
        """Одобрение обходного решения"""
        workaround = self.workarounds.get(workaround_id)
        if not workaround:
            return False
            
        workaround.is_approved = True
        return True
        
    async def create_known_error(self, problem_id: str,
                                title: str,
                                description: str,
                                symptoms: List[str],
                                workaround_id: Optional[str] = None) -> Optional[KnownError]:
        """Создание известной ошибки"""
        problem = self.problems.get(problem_id)
        if not problem:
            return None
            
        ke = KnownError(
            ke_id=f"ke_{uuid.uuid4().hex[:8]}",
            problem_id=problem_id,
            title=title,
            description=description,
            symptoms=symptoms,
            root_cause=problem.root_cause,
            workaround_id=workaround_id
        )
        
        self.known_errors[ke.ke_id] = ke
        problem.known_error_id = ke.ke_id
        problem.status = ProblemStatus.KNOWN_ERROR
        
        return ke
        
    async def resolve_problem(self, problem_id: str,
                             resolution: str,
                             permanent_fix: str = "") -> bool:
        """Решение проблемы"""
        problem = self.problems.get(problem_id)
        if not problem:
            return False
            
        problem.resolution = resolution
        problem.permanent_fix = permanent_fix
        problem.status = ProblemStatus.RESOLVED
        problem.resolved_at = datetime.now()
        
        # Update known error if exists
        if problem.known_error_id:
            ke = self.known_errors.get(problem.known_error_id)
            if ke:
                ke.resolution_status = "resolved"
                
        return True
        
    async def close_problem(self, problem_id: str,
                           prevention_actions: List[str] = None) -> bool:
        """Закрытие проблемы"""
        problem = self.problems.get(problem_id)
        if not problem:
            return False
            
        if prevention_actions:
            problem.prevention_actions = prevention_actions
            
        problem.status = ProblemStatus.CLOSED
        problem.closed_at = datetime.now()
        
        return True
        
    async def analyze_trends(self, days: int = 30) -> List[TrendPattern]:
        """Анализ трендов"""
        cutoff = datetime.now() - timedelta(days=days)
        
        category_counts: Dict[ProblemCategory, Dict[str, Any]] = {}
        
        for problem in self.problems.values():
            if problem.detected_at < cutoff:
                continue
                
            if problem.category not in category_counts:
                category_counts[problem.category] = {
                    "count": 0,
                    "incidents": 0,
                    "users": 0
                }
                
            category_counts[problem.category]["count"] += 1
            category_counts[problem.category]["incidents"] += len(problem.related_incidents)
            category_counts[problem.category]["users"] += problem.affected_users
            
        trends = []
        for category, data in category_counts.items():
            if data["count"] >= 2:  # Pattern threshold
                trend = TrendPattern(
                    pattern_id=f"trend_{uuid.uuid4().hex[:8]}",
                    category=category,
                    description=f"Recurring {category.value} problems detected",
                    occurrence_count=data["count"],
                    time_period_days=days,
                    total_incidents=data["incidents"],
                    total_affected_users=data["users"],
                    recommendation=f"Consider proactive {category.value} review"
                )
                trends.append(trend)
                self.trends[trend.pattern_id] = trend
                
        return trends
        
    def search_known_errors(self, symptoms: List[str]) -> List[KnownError]:
        """Поиск известных ошибок по симптомам"""
        results = []
        
        for ke in self.known_errors.values():
            match_score = 0
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                for ke_symptom in ke.symptoms:
                    if symptom_lower in ke_symptom.lower():
                        match_score += 1
                        break
                        
            if match_score > 0:
                results.append((ke, match_score))
                
        # Sort by match score
        results.sort(key=lambda x: x[1], reverse=True)
        return [ke for ke, _ in results]
        
    def get_problem_details(self, problem_id: str) -> Dict[str, Any]:
        """Получение деталей проблемы"""
        problem = self.problems.get(problem_id)
        if not problem:
            return {}
            
        # Get related incidents
        incidents = [
            self.incidents.get(i_id)
            for i_id in problem.related_incidents
            if self.incidents.get(i_id)
        ]
        
        # Get RCA
        rca = self.rcas.get(problem.rca_id) if problem.rca_id else None
        
        # Get workarounds
        workarounds = [
            self.workarounds.get(w_id)
            for w_id in problem.workaround_ids
            if self.workarounds.get(w_id)
        ]
        
        # Get known error
        ke = self.known_errors.get(problem.known_error_id) if problem.known_error_id else None
        
        # Calculate metrics
        total_duration = sum(i.duration_minutes for i in incidents)
        
        return {
            "problem_id": problem_id,
            "title": problem.title,
            "description": problem.description,
            "category": problem.category.value,
            "priority": problem.priority.value,
            "status": problem.status.value,
            "assigned_to": problem.assigned_to,
            "team": problem.team,
            "related_incidents_count": len(incidents),
            "total_incident_duration_minutes": total_duration,
            "affected_users": problem.affected_users,
            "affected_services": problem.affected_services,
            "root_cause": problem.root_cause,
            "rca_status": rca.status if rca else "not_started",
            "rca_method": rca.method.value if rca else None,
            "workarounds_count": len(workarounds),
            "has_known_error": ke is not None,
            "resolution": problem.resolution,
            "prevention_actions": problem.prevention_actions,
            "detected_at": problem.detected_at.isoformat(),
            "resolved_at": problem.resolved_at.isoformat() if problem.resolved_at else None
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = {}
        by_category = {}
        by_priority = {}
        
        total_affected = 0
        resolved_count = 0
        
        for problem in self.problems.values():
            by_status[problem.status.value] = by_status.get(problem.status.value, 0) + 1
            by_category[problem.category.value] = by_category.get(problem.category.value, 0) + 1
            by_priority[problem.priority.value] = by_priority.get(problem.priority.value, 0) + 1
            
            total_affected += problem.affected_users
            
            if problem.status in [ProblemStatus.RESOLVED, ProblemStatus.CLOSED]:
                resolved_count += 1
                
        # Calculate MTTR for resolved problems
        resolved_times = []
        for problem in self.problems.values():
            if problem.resolved_at:
                time_to_resolve = (problem.resolved_at - problem.detected_at).total_seconds() / 3600
                resolved_times.append(time_to_resolve)
                
        avg_resolution_time = sum(resolved_times) / len(resolved_times) if resolved_times else 0
        
        return {
            "total_problems": len(self.problems),
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
            "total_rcas": len(self.rcas),
            "completed_rcas": sum(1 for r in self.rcas.values() if r.status == "completed"),
            "total_workarounds": len(self.workarounds),
            "approved_workarounds": sum(1 for w in self.workarounds.values() if w.is_approved),
            "total_known_errors": len(self.known_errors),
            "total_linked_incidents": len(self.incidents),
            "total_affected_users": total_affected,
            "resolved_problems": resolved_count,
            "avg_resolution_time_hours": avg_resolution_time,
            "detected_trends": len(self.trends)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 305: Problem Management Platform")
    print("=" * 60)
    
    manager = ProblemManagementManager()
    print("✓ Problem Management Manager created")
    
    # Create problems
    print("\n🔴 Creating Problems...")
    
    problems_data = [
        ("Database Connection Pool Exhaustion", "Recurring database connection exhaustion during peak hours",
         ProblemCategory.DATABASE, ProblemPriority.HIGH, ["User Service", "Order Service"]),
        ("Intermittent API Timeouts", "Random timeouts on API calls to payment service",
         ProblemCategory.NETWORK, ProblemPriority.CRITICAL, ["Payment Service"]),
        ("Memory Leak in Worker Process", "Memory consumption grows over time in worker nodes",
         ProblemCategory.SOFTWARE, ProblemPriority.MEDIUM, ["Background Jobs"]),
        ("SSL Certificate Renewal Failures", "Automated certificate renewal failing intermittently",
         ProblemCategory.SECURITY, ProblemPriority.HIGH, ["API Gateway", "CDN"]),
        ("Disk Space Issues on Log Server", "Log server running out of space frequently",
         ProblemCategory.CAPACITY, ProblemPriority.MEDIUM, ["Logging Infrastructure"]),
        ("Cache Invalidation Lag", "Cache updates not propagating consistently across nodes",
         ProblemCategory.SOFTWARE, ProblemPriority.MEDIUM, ["Cache Cluster"]),
        ("Configuration Drift in Production", "Configuration differences between prod instances",
         ProblemCategory.CONFIGURATION, ProblemPriority.LOW, ["All Services"])
    ]
    
    problems = []
    for title, desc, category, priority, services in problems_data:
        problem = await manager.create_problem(title, desc, category, priority, services)
        problems.append(problem)
        print(f"  🔴 [{priority.value.upper()}] {title}")
        
    # Link incidents to problems
    print("\n🔗 Linking Incidents...")
    
    incident_data = [
        (problems[0], "INC001", "DB Connection Timeout", "high", 500, 15),
        (problems[0], "INC002", "Service Unavailable - User Service", "critical", 1200, 25),
        (problems[0], "INC003", "Database Error Spike", "medium", 300, 10),
        (problems[1], "INC004", "Payment Processing Failure", "critical", 800, 45),
        (problems[1], "INC005", "API Gateway Timeout", "high", 450, 20),
        (problems[2], "INC006", "Worker Node OOM Kill", "high", 200, 30),
        (problems[3], "INC007", "SSL Handshake Failures", "critical", 2000, 60),
        (problems[4], "INC008", "Log Shipping Stopped", "medium", 0, 120)
    ]
    
    for problem, inc_id, title, severity, users, duration in incident_data:
        await manager.link_incident(problem.problem_id, inc_id, title, severity, users, duration)
        
    print(f"  ✓ Linked {len(incident_data)} incidents to problems")
    
    # Assign problems
    print("\n👤 Assigning Problems...")
    
    assignments = [
        (problems[0], "John Smith", "Database Team"),
        (problems[1], "Alice Chen", "Platform Team"),
        (problems[2], "Bob Wilson", "Backend Team"),
        (problems[3], "Carol Davis", "Security Team"),
        (problems[4], "David Lee", "Infrastructure Team")
    ]
    
    for problem, assignee, team in assignments:
        await manager.assign_problem(problem.problem_id, assignee, team)
        print(f"  👤 {problem.title[:40]}... → {assignee}")
        
    # Start Root Cause Analysis
    print("\n🔍 Starting Root Cause Analysis...")
    
    rca_data = [
        (problems[0], RCAMethod.FIVE_WHYS),
        (problems[1], RCAMethod.TIMELINE),
        (problems[2], RCAMethod.FISHBONE),
        (problems[3], RCAMethod.FAULT_TREE)
    ]
    
    rcas = []
    for problem, method in rca_data:
        rca = await manager.start_rca(problem.problem_id, method)
        rcas.append(rca)
        print(f"  🔍 {problem.title[:40]}... - {method.value}")
        
    # Complete some RCAs
    print("\n✅ Completing RCA...")
    
    rca_results = [
        (rcas[0], "Connection pool size insufficient for peak load; max_connections set too low"),
        (rcas[1], "Network latency spike caused by faulty switch in datacenter rack"),
        (rcas[2], "Memory leak in JSON serialization library version 2.3.1")
    ]
    
    for rca, root_cause in rca_results:
        await manager.update_rca(
            rca.rca_id,
            root_cause=root_cause,
            contributing_factors=["Configuration oversight", "Missing monitoring"],
            evidence=["Log analysis", "Metrics review", "Code inspection"]
        )
        await manager.complete_rca(rca.rca_id, root_cause)
        
        problem = manager.problems.get(rca.problem_id)
        print(f"\n  ✅ {problem.title[:35]}...")
        print(f"     Root Cause: {root_cause[:50]}...")
        
    # Create workarounds
    print("\n🛠️ Creating Workarounds...")
    
    workarounds_data = [
        (problems[0], "Increase Connection Pool", "Temporarily increase pool size",
         ["Update connection pool max to 200", "Restart affected services", "Monitor connection count"],
         85.0),
        (problems[1], "Enable Retry Logic", "Add retry with exponential backoff",
         ["Enable retry policy", "Set max retries to 3", "Configure backoff interval"],
         70.0),
        (problems[2], "Scheduled Restart", "Restart workers every 4 hours",
         ["Configure scheduled job", "Set restart interval to 4h", "Enable graceful shutdown"],
         90.0),
        (problems[4], "Log Rotation", "Implement aggressive log rotation",
         ["Set rotation to 1GB", "Keep max 5 files", "Enable compression"],
         95.0)
    ]
    
    for problem, title, desc, steps, effectiveness in workarounds_data:
        workaround = await manager.create_workaround(
            problem.problem_id, title, desc, steps, effectiveness
        )
        await manager.approve_workaround(workaround.workaround_id)
        print(f"  🛠️ {title} ({effectiveness:.0f}% effective)")
        
    # Create known errors
    print("\n📚 Creating Known Errors...")
    
    ke_data = [
        (problems[0], "KEDB-001: Connection Pool Exhaustion",
         "Database connection pool exhaustion under load",
         ["Connection timeout errors", "Service degradation at peak", "Pool wait queue growth"]),
        (problems[2], "KEDB-002: Worker Memory Leak",
         "Memory leak in worker process affecting long-running jobs",
         ["Gradual memory increase", "OOM kills after ~4 hours", "High swap usage"])
    ]
    
    for problem, title, desc, symptoms in ke_data:
        workaround_id = problem.workaround_ids[0] if problem.workaround_ids else None
        ke = await manager.create_known_error(
            problem.problem_id, title, desc, symptoms, workaround_id
        )
        print(f"  📚 {title}")
        
    # Resolve some problems
    print("\n✅ Resolving Problems...")
    
    resolutions = [
        (problems[0], "Increased pool size and added connection recycling", "Connection pool configuration update"),
        (problems[2], "Updated JSON library to version 2.4.0 which fixes the leak", "Library upgrade deployed")
    ]
    
    for problem, resolution, fix in resolutions:
        await manager.resolve_problem(problem.problem_id, resolution, fix)
        print(f"  ✅ {problem.title[:45]}...")
        
    # Close resolved problems
    print("\n🔒 Closing Problems...")
    
    await manager.close_problem(problems[0].problem_id, [
        "Add connection pool monitoring alerts",
        "Document pool sizing guidelines",
        "Schedule quarterly capacity review"
    ])
    print(f"  🔒 {problems[0].title[:45]}...")
    
    # Analyze trends
    print("\n📊 Analyzing Trends...")
    
    trends = await manager.analyze_trends(30)
    
    for trend in trends:
        print(f"\n  📊 {trend.category.value.upper()} Pattern")
        print(f"     Occurrences: {trend.occurrence_count} in {trend.time_period_days} days")
        print(f"     Impact: {trend.total_incidents} incidents, {trend.total_affected_users} users")
        print(f"     Recommendation: {trend.recommendation}")
        
    # Search known errors
    print("\n🔍 Searching Known Errors...")
    
    search_symptoms = ["memory", "OOM"]
    results = manager.search_known_errors(search_symptoms)
    
    print(f"  Searching for: {search_symptoms}")
    for ke in results:
        print(f"  📚 Found: {ke.title}")
        
    # Problem details
    print("\n📋 Problem Details:")
    
    for problem in problems[:4]:
        details = manager.get_problem_details(problem.problem_id)
        
        priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        
        print(f"\n  {priority_icons.get(details['priority'], '⚪')} {details['title'][:50]}")
        print(f"     Status: {details['status']} | Category: {details['category']}")
        print(f"     Incidents: {details['related_incidents_count']} | Affected: {details['affected_users']} users")
        print(f"     RCA: {details['rca_status']} | Workarounds: {details['workarounds_count']}")
        
        if details['root_cause']:
            print(f"     Root Cause: {details['root_cause'][:50]}...")
            
    # Problem board
    print("\n📊 Problem Board:")
    
    print("\n  ┌──────────────────────────────────────────┬──────────┬──────────────────┬──────────┐")
    print("  │ Problem                                  │ Priority │ Status           │ Incidents│")
    print("  ├──────────────────────────────────────────┼──────────┼──────────────────┼──────────┤")
    
    for problem in problems:
        title = problem.title[:40].ljust(40)
        
        priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        priority = f"{priority_icons.get(problem.priority.value, '⚪')} {problem.priority.value[:6]}".ljust(8)
        
        status = problem.status.value[:16].ljust(16)
        incidents = str(len(problem.related_incidents)).ljust(8)
        
        print(f"  │ {title} │ {priority} │ {status} │ {incidents} │")
        
    print("  └──────────────────────────────────────────┴──────────┴──────────────────┴──────────┘")
    
    # Statistics
    print("\n📊 Problem Management Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Problems: {stats['total_problems']}")
    
    print("\n  By Status:")
    for status, count in stats['by_status'].items():
        bar = "█" * min(count, 8) + "░" * (8 - min(count, 8))
        print(f"    {status:25} [{bar}] {count}")
        
    print("\n  By Priority:")
    for priority, count in stats['by_priority'].items():
        print(f"    {priority}: {count}")
        
    print(f"\n  Root Cause Analyses: {stats['total_rcas']} ({stats['completed_rcas']} completed)")
    print(f"  Workarounds: {stats['total_workarounds']} ({stats['approved_workarounds']} approved)")
    print(f"  Known Errors: {stats['total_known_errors']}")
    print(f"  Linked Incidents: {stats['total_linked_incidents']}")
    print(f"  Total Affected Users: {stats['total_affected_users']}")
    print(f"  Avg Resolution Time: {stats['avg_resolution_time_hours']:.1f} hours")
    
    resolution_rate = (stats['resolved_problems'] / max(stats['total_problems'], 1)) * 100
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   Problem Management Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Problems:              {stats['total_problems']:>12}                          │")
    print(f"│ Resolved Problems:           {stats['resolved_problems']:>12}                          │")
    print(f"│ Known Errors Documented:     {stats['total_known_errors']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Resolution Rate:             {resolution_rate:>11.1f}%                          │")
    print(f"│ Avg Resolution Time:         {stats['avg_resolution_time_hours']:>10.1f}h                          │")
    print(f"│ Affected Users:              {stats['total_affected_users']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Problem Management Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
