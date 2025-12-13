#!/usr/bin/env python3
"""
Server Init - Iteration 52: Compliance & Policy Automation
Автоматизация соответствия и политик

Функционал:
- Compliance Frameworks - фреймворки соответствия (SOC2, GDPR, HIPAA, PCI-DSS)
- Policy Engine - движок политик
- Automated Auditing - автоматический аудит
- Evidence Collection - сбор доказательств
- Risk Assessment - оценка рисков
- Remediation Automation - автоматическое исправление
- Compliance Reporting - отчёты о соответствии
- Continuous Compliance - непрерывное соответствие
"""

import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid


class ComplianceFramework(Enum):
    """Фреймворк соответствия"""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    CIS = "cis"
    FedRAMP = "fedramp"


class ControlStatus(Enum):
    """Статус контроля"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    NOT_ASSESSED = "not_assessed"


class RiskLevel(Enum):
    """Уровень риска"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class PolicyType(Enum):
    """Тип политики"""
    SECURITY = "security"
    ACCESS = "access"
    DATA = "data"
    NETWORK = "network"
    ENCRYPTION = "encryption"
    AUDIT = "audit"
    RETENTION = "retention"
    CUSTOM = "custom"


class RemediationStatus(Enum):
    """Статус исправления"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AuditStatus(Enum):
    """Статус аудита"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Control:
    """Контроль соответствия"""
    control_id: str
    name: str
    framework: ComplianceFramework
    
    # Описание
    description: str = ""
    category: str = ""
    
    # Требования
    requirements: List[str] = field(default_factory=list)
    
    # Статус
    status: ControlStatus = ControlStatus.NOT_ASSESSED
    
    # Проверка
    check_query: str = ""  # Query для автоматической проверки
    
    # Последняя проверка
    last_assessed: Optional[datetime] = None
    next_assessment: Optional[datetime] = None
    
    # Доказательства
    evidence_required: List[str] = field(default_factory=list)


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str
    policy_type: PolicyType
    
    # Правило
    rule: str = ""  # OPA/Rego policy
    
    # Применение
    scope: List[str] = field(default_factory=list)  # Resources/namespaces
    
    # Enforcement
    enforcement_mode: str = "audit"  # audit, warn, deny
    
    # Статус
    enabled: bool = True
    
    # Метрики
    violations_count: int = 0
    last_violation: Optional[datetime] = None
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyViolation:
    """Нарушение политики"""
    violation_id: str
    policy_id: str
    
    # Ресурс
    resource_id: str = ""
    resource_type: str = ""
    
    # Детали
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Риск
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Статус
    remediation_status: RemediationStatus = RemediationStatus.PENDING
    
    # Время
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class Evidence:
    """Доказательство соответствия"""
    evidence_id: str
    control_id: str
    
    # Тип
    evidence_type: str = ""  # screenshot, log, config, report
    
    # Содержимое
    title: str = ""
    description: str = ""
    content: str = ""
    
    # Файл
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Время
    collected_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Автор
    collected_by: str = "system"


@dataclass
class RiskAssessment:
    """Оценка риска"""
    assessment_id: str
    name: str
    
    # Скоп
    scope: List[str] = field(default_factory=list)
    
    # Результаты
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    
    # Score
    risk_score: float = 0.0  # 0-100
    
    # Время
    assessed_at: datetime = field(default_factory=datetime.now)
    
    # Рекомендации
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Audit:
    """Аудит"""
    audit_id: str
    name: str
    framework: ComplianceFramework
    
    # Скоп
    controls: List[str] = field(default_factory=list)
    
    # Статус
    status: AuditStatus = AuditStatus.SCHEDULED
    
    # Результаты
    compliant_count: int = 0
    non_compliant_count: int = 0
    
    # Время
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Отчёт
    report_path: Optional[str] = None


@dataclass
class RemediationTask:
    """Задача исправления"""
    task_id: str
    violation_id: str
    
    # Описание
    title: str = ""
    description: str = ""
    
    # Автоматизация
    auto_remediation: bool = False
    remediation_script: str = ""
    
    # Статус
    status: RemediationStatus = RemediationStatus.PENDING
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Результат
    result: Optional[str] = None
    error: Optional[str] = None


class ComplianceEngine:
    """Движок соответствия"""
    
    def __init__(self):
        self.controls: Dict[str, Control] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.audits: Dict[str, Audit] = {}
        
        # Загрузка стандартных контролей
        self._load_framework_controls()
        
    def _load_framework_controls(self):
        """Загрузка контролей фреймворков"""
        # SOC2 контроли
        soc2_controls = [
            ("CC1.1", "Control Environment", "Organization demonstrates commitment to integrity"),
            ("CC2.1", "Information Communication", "Security policies are communicated"),
            ("CC3.1", "Risk Assessment", "Risk assessment processes are defined"),
            ("CC4.1", "Monitoring Activities", "Continuous monitoring is implemented"),
            ("CC5.1", "Logical Access Controls", "Logical access is restricted"),
            ("CC6.1", "System Operations", "Security events are detected and analyzed"),
            ("CC7.1", "Change Management", "Changes are controlled and authorized"),
            ("CC8.1", "Risk Mitigation", "Risks are identified and mitigated")
        ]
        
        for ctrl_id, name, desc in soc2_controls:
            self.controls[f"soc2_{ctrl_id}"] = Control(
                control_id=f"soc2_{ctrl_id}",
                name=name,
                framework=ComplianceFramework.SOC2,
                description=desc,
                category=ctrl_id.split('.')[0]
            )
            
        # GDPR контроли
        gdpr_controls = [
            ("Art5", "Data Processing Principles", "Lawfulness, fairness, transparency"),
            ("Art6", "Lawfulness of Processing", "Legal basis for processing"),
            ("Art7", "Consent", "Conditions for valid consent"),
            ("Art12", "Transparent Information", "Clear privacy information"),
            ("Art17", "Right to Erasure", "Right to be forgotten"),
            ("Art25", "Privacy by Design", "Data protection by design"),
            ("Art32", "Security of Processing", "Appropriate security measures"),
            ("Art33", "Breach Notification", "72-hour notification requirement")
        ]
        
        for ctrl_id, name, desc in gdpr_controls:
            self.controls[f"gdpr_{ctrl_id}"] = Control(
                control_id=f"gdpr_{ctrl_id}",
                name=name,
                framework=ComplianceFramework.GDPR,
                description=desc,
                category="GDPR"
            )
            
    async def assess_control(self, control_id: str) -> Dict[str, Any]:
        """Оценка контроля"""
        control = self.controls.get(control_id)
        if not control:
            return {"error": "Control not found"}
            
        # Симуляция оценки
        await asyncio.sleep(0.05)
        
        # Случайный результат для демонстрации
        rand = random.random()
        if rand > 0.7:
            control.status = ControlStatus.COMPLIANT
        elif rand > 0.4:
            control.status = ControlStatus.PARTIALLY_COMPLIANT
        else:
            control.status = ControlStatus.NON_COMPLIANT
            
        control.last_assessed = datetime.now()
        control.next_assessment = datetime.now() + timedelta(days=30)
        
        return {
            "control_id": control_id,
            "status": control.status.value,
            "last_assessed": control.last_assessed.isoformat()
        }
        
    def add_evidence(self, control_id: str, evidence_type: str,
                      title: str, content: str, **kwargs) -> Evidence:
        """Добавление доказательства"""
        evidence = Evidence(
            evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            content=content,
            **kwargs
        )
        
        self.evidence[evidence.evidence_id] = evidence
        return evidence
        
    async def run_audit(self, framework: ComplianceFramework) -> Audit:
        """Запуск аудита"""
        # Получение контролей фреймворка
        framework_controls = [
            c for c in self.controls.values()
            if c.framework == framework
        ]
        
        audit = Audit(
            audit_id=f"audit_{uuid.uuid4().hex[:8]}",
            name=f"{framework.value.upper()} Compliance Audit",
            framework=framework,
            controls=[c.control_id for c in framework_controls],
            status=AuditStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.audits[audit.audit_id] = audit
        
        # Оценка каждого контроля
        for control in framework_controls:
            await self.assess_control(control.control_id)
            
            if control.status == ControlStatus.COMPLIANT:
                audit.compliant_count += 1
            else:
                audit.non_compliant_count += 1
                
        audit.status = AuditStatus.COMPLETED
        audit.completed_at = datetime.now()
        
        return audit
        
    def get_compliance_score(self, framework: Optional[ComplianceFramework] = None) -> Dict[str, Any]:
        """Получение score соответствия"""
        controls = list(self.controls.values())
        
        if framework:
            controls = [c for c in controls if c.framework == framework]
            
        assessed = [c for c in controls if c.status != ControlStatus.NOT_ASSESSED]
        compliant = [c for c in assessed if c.status == ControlStatus.COMPLIANT]
        partial = [c for c in assessed if c.status == ControlStatus.PARTIALLY_COMPLIANT]
        
        total = len(assessed)
        score = 0
        
        if total > 0:
            score = ((len(compliant) + len(partial) * 0.5) / total) * 100
            
        return {
            "framework": framework.value if framework else "all",
            "total_controls": len(controls),
            "assessed": len(assessed),
            "compliant": len(compliant),
            "partially_compliant": len(partial),
            "non_compliant": total - len(compliant) - len(partial),
            "score": round(score, 1)
        }


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.violations: Dict[str, PolicyViolation] = {}
        
    def create_policy(self, name: str, policy_type: PolicyType,
                       rule: str, **kwargs) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            policy_type=policy_type,
            rule=rule,
            **kwargs
        )
        
        self.policies[policy.policy_id] = policy
        return policy
        
    async def evaluate_policy(self, policy_id: str,
                               resource: Dict[str, Any]) -> Dict[str, Any]:
        """Оценка политики"""
        policy = self.policies.get(policy_id)
        if not policy or not policy.enabled:
            return {"compliant": True}
            
        # Симуляция проверки политики
        await asyncio.sleep(0.01)
        
        # Случайный результат для демонстрации
        compliant = random.random() > 0.3
        
        result = {
            "policy_id": policy_id,
            "policy_name": policy.name,
            "resource_id": resource.get("id", "unknown"),
            "compliant": compliant,
            "enforcement_mode": policy.enforcement_mode
        }
        
        if not compliant:
            violation = PolicyViolation(
                violation_id=f"viol_{uuid.uuid4().hex[:8]}",
                policy_id=policy_id,
                resource_id=resource.get("id", ""),
                resource_type=resource.get("type", ""),
                message=f"Resource violates policy: {policy.name}",
                details=resource,
                risk_level=RiskLevel.MEDIUM
            )
            
            self.violations[violation.violation_id] = violation
            policy.violations_count += 1
            policy.last_violation = datetime.now()
            
            result["violation_id"] = violation.violation_id
            result["message"] = violation.message
            
        return result
        
    async def scan_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Сканирование ресурсов"""
        results = []
        
        for resource in resources:
            for policy in self.policies.values():
                if policy.enabled:
                    result = await self.evaluate_policy(policy.policy_id, resource)
                    results.append(result)
                    
        return results
        
    def get_violations(self, status: Optional[RemediationStatus] = None) -> List[PolicyViolation]:
        """Получение нарушений"""
        violations = list(self.violations.values())
        
        if status:
            violations = [v for v in violations if v.remediation_status == status]
            
        return sorted(violations, key=lambda v: v.detected_at, reverse=True)
        
    def get_policy_stats(self) -> Dict[str, Any]:
        """Статистика политик"""
        total_policies = len(self.policies)
        enabled_policies = len([p for p in self.policies.values() if p.enabled])
        total_violations = len(self.violations)
        
        by_type = defaultdict(int)
        for p in self.policies.values():
            by_type[p.policy_type.value] += 1
            
        by_risk = defaultdict(int)
        for v in self.violations.values():
            by_risk[v.risk_level.value] += 1
            
        return {
            "policies": {
                "total": total_policies,
                "enabled": enabled_policies,
                "by_type": dict(by_type)
            },
            "violations": {
                "total": total_violations,
                "pending": len([v for v in self.violations.values() if v.remediation_status == RemediationStatus.PENDING]),
                "by_risk": dict(by_risk)
            }
        }


class RemediationEngine:
    """Движок исправлений"""
    
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.tasks: Dict[str, RemediationTask] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, policy_type: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[policy_type] = handler
        
    async def create_remediation(self, violation_id: str,
                                  auto: bool = False) -> RemediationTask:
        """Создание задачи исправления"""
        violation = self.policy_engine.violations.get(violation_id)
        if not violation:
            raise ValueError("Violation not found")
            
        policy = self.policy_engine.policies.get(violation.policy_id)
        
        task = RemediationTask(
            task_id=f"rem_{uuid.uuid4().hex[:8]}",
            violation_id=violation_id,
            title=f"Remediate: {violation.message}",
            description=f"Fix violation of policy: {policy.name if policy else 'Unknown'}",
            auto_remediation=auto
        )
        
        self.tasks[task.task_id] = task
        
        if auto:
            await self.execute_remediation(task.task_id)
            
        return task
        
    async def execute_remediation(self, task_id: str) -> RemediationTask:
        """Выполнение исправления"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")
            
        task.status = RemediationStatus.IN_PROGRESS
        
        try:
            # Симуляция исправления
            await asyncio.sleep(0.1)
            
            # 90% успех
            if random.random() > 0.1:
                task.status = RemediationStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = "Remediation applied successfully"
                
                # Обновление violation
                violation = self.policy_engine.violations.get(task.violation_id)
                if violation:
                    violation.remediation_status = RemediationStatus.COMPLETED
                    violation.resolved_at = datetime.now()
            else:
                task.status = RemediationStatus.FAILED
                task.error = "Failed to apply remediation"
                
        except Exception as e:
            task.status = RemediationStatus.FAILED
            task.error = str(e)
            
        return task
        
    async def auto_remediate_all(self) -> List[RemediationTask]:
        """Автоматическое исправление всех нарушений"""
        pending_violations = self.policy_engine.get_violations(RemediationStatus.PENDING)
        tasks = []
        
        for violation in pending_violations:
            task = await self.create_remediation(violation.violation_id, auto=True)
            tasks.append(task)
            
        return tasks


class RiskManager:
    """Менеджер рисков"""
    
    def __init__(self, compliance_engine: ComplianceEngine,
                  policy_engine: PolicyEngine):
        self.compliance_engine = compliance_engine
        self.policy_engine = policy_engine
        self.assessments: Dict[str, RiskAssessment] = {}
        
    async def assess_risk(self, scope: List[str] = None) -> RiskAssessment:
        """Оценка риска"""
        assessment = RiskAssessment(
            assessment_id=f"risk_{uuid.uuid4().hex[:8]}",
            name=f"Risk Assessment {datetime.now().strftime('%Y-%m-%d')}",
            scope=scope or ["all"]
        )
        
        # Подсчёт рисков из violations
        for violation in self.policy_engine.violations.values():
            assessment.total_risks += 1
            
            if violation.risk_level == RiskLevel.CRITICAL:
                assessment.critical_risks += 1
            elif violation.risk_level == RiskLevel.HIGH:
                assessment.high_risks += 1
            elif violation.risk_level == RiskLevel.MEDIUM:
                assessment.medium_risks += 1
            else:
                assessment.low_risks += 1
                
        # Расчёт risk score
        if assessment.total_risks > 0:
            weighted_score = (
                assessment.critical_risks * 40 +
                assessment.high_risks * 25 +
                assessment.medium_risks * 10 +
                assessment.low_risks * 5
            )
            assessment.risk_score = min(100, weighted_score)
            
        # Генерация рекомендаций
        if assessment.critical_risks > 0:
            assessment.recommendations.append("Немедленно устраните критические риски")
        if assessment.high_risks > 0:
            assessment.recommendations.append("Приоритизируйте устранение высоких рисков")
        if assessment.risk_score > 70:
            assessment.recommendations.append("Общий уровень риска высокий - требуется план действий")
            
        self.assessments[assessment.assessment_id] = assessment
        return assessment


class ComplianceReporter:
    """Генератор отчётов"""
    
    def __init__(self, compliance_engine: ComplianceEngine,
                  policy_engine: PolicyEngine,
                  risk_manager: RiskManager):
        self.compliance_engine = compliance_engine
        self.policy_engine = policy_engine
        self.risk_manager = risk_manager
        
    def generate_compliance_report(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Генерация отчёта о соответствии"""
        score = self.compliance_engine.get_compliance_score(framework)
        
        controls = [
            c for c in self.compliance_engine.controls.values()
            if c.framework == framework
        ]
        
        control_details = []
        for control in controls:
            evidence_count = len([
                e for e in self.compliance_engine.evidence.values()
                if e.control_id == control.control_id
            ])
            
            control_details.append({
                "control_id": control.control_id,
                "name": control.name,
                "status": control.status.value,
                "last_assessed": control.last_assessed.isoformat() if control.last_assessed else None,
                "evidence_count": evidence_count
            })
            
        return {
            "framework": framework.value,
            "generated_at": datetime.now().isoformat(),
            "summary": score,
            "controls": control_details,
            "recommendations": self._generate_recommendations(score)
        }
        
    def _generate_recommendations(self, score: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []
        
        if score["non_compliant"] > 0:
            recommendations.append(f"Устраните {score['non_compliant']} несоответствующих контролей")
            
        if score["score"] < 80:
            recommendations.append("Общий уровень соответствия ниже целевого (80%)")
            
        if score["assessed"] < score["total_controls"]:
            not_assessed = score["total_controls"] - score["assessed"]
            recommendations.append(f"Проведите оценку для {not_assessed} непроверенных контролей")
            
        return recommendations
        
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Генерация executive summary"""
        policy_stats = self.policy_engine.get_policy_stats()
        
        # Compliance scores по фреймворкам
        framework_scores = {}
        for framework in ComplianceFramework:
            score = self.compliance_engine.get_compliance_score(framework)
            if score["assessed"] > 0:
                framework_scores[framework.value] = score["score"]
                
        return {
            "generated_at": datetime.now().isoformat(),
            "overall_compliance": {
                "frameworks_monitored": len(framework_scores),
                "average_score": round(sum(framework_scores.values()) / max(len(framework_scores), 1), 1),
                "by_framework": framework_scores
            },
            "policy_status": {
                "total_policies": policy_stats["policies"]["total"],
                "active_violations": policy_stats["violations"]["pending"],
                "violations_by_risk": policy_stats["violations"]["by_risk"]
            },
            "risk_summary": {
                "overall_risk_level": self._calculate_overall_risk(policy_stats)
            }
        }
        
    def _calculate_overall_risk(self, stats: Dict[str, Any]) -> str:
        """Расчёт общего уровня риска"""
        violations = stats["violations"]["by_risk"]
        
        if violations.get("critical", 0) > 0:
            return "critical"
        elif violations.get("high", 0) > 0:
            return "high"
        elif violations.get("medium", 0) > 0:
            return "medium"
        else:
            return "low"


class CompliancePlatform:
    """Платформа соответствия и политик"""
    
    def __init__(self):
        self.compliance_engine = ComplianceEngine()
        self.policy_engine = PolicyEngine()
        self.remediation_engine = RemediationEngine(self.policy_engine)
        self.risk_manager = RiskManager(self.compliance_engine, self.policy_engine)
        self.reporter = ComplianceReporter(
            self.compliance_engine,
            self.policy_engine,
            self.risk_manager
        )
        
    def get_status(self) -> Dict[str, Any]:
        """Статус платформы"""
        return {
            "compliance": {
                "controls": len(self.compliance_engine.controls),
                "evidence": len(self.compliance_engine.evidence),
                "audits": len(self.compliance_engine.audits)
            },
            "policies": self.policy_engine.get_policy_stats(),
            "remediations": {
                "total": len(self.remediation_engine.tasks),
                "completed": len([t for t in self.remediation_engine.tasks.values() if t.status == RemediationStatus.COMPLETED])
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 52: Compliance & Policy Automation")
    print("=" * 60)
    
    async def demo():
        # Создание платформы
        platform = CompliancePlatform()
        print("✓ Compliance Platform created")
        
        # Compliance контроли
        print("\n📋 Compliance Controls:")
        
        controls = platform.compliance_engine.controls
        frameworks = defaultdict(int)
        for control in controls.values():
            frameworks[control.framework.value] += 1
            
        for fw, count in frameworks.items():
            print(f"  {fw.upper()}: {count} controls")
            
        # Оценка контролей
        print("\n🔍 Assessing controls...")
        
        for control_id in list(controls.keys())[:5]:
            result = await platform.compliance_engine.assess_control(control_id)
            control = controls[control_id]
            print(f"  {control.name}: {result['status']}")
            
        # Аудит
        print("\n📝 Running SOC2 audit...")
        
        audit = await platform.compliance_engine.run_audit(ComplianceFramework.SOC2)
        print(f"  Audit ID: {audit.audit_id}")
        print(f"  Compliant: {audit.compliant_count}")
        print(f"  Non-compliant: {audit.non_compliant_count}")
        
        # Score
        score = platform.compliance_engine.get_compliance_score(ComplianceFramework.SOC2)
        print(f"  Compliance Score: {score['score']}%")
        
        # Добавление evidence
        print("\n📎 Adding evidence...")
        
        ev1 = platform.compliance_engine.add_evidence(
            control_id="soc2_CC5.1",
            evidence_type="config",
            title="Access Control Configuration",
            content="IAM Policy restricting access..."
        )
        print(f"  ✓ Added: {ev1.title}")
        
        ev2 = platform.compliance_engine.add_evidence(
            control_id="soc2_CC6.1",
            evidence_type="log",
            title="Security Event Logs",
            content="Sample security event logs..."
        )
        print(f"  ✓ Added: {ev2.title}")
        
        # Политики
        print("\n📜 Creating policies...")
        
        pol1 = platform.policy_engine.create_policy(
            name="require-encryption",
            policy_type=PolicyType.ENCRYPTION,
            rule='deny { not input.encrypted }',
            scope=["s3-buckets", "databases"],
            enforcement_mode="deny"
        )
        print(f"  ✓ Created: {pol1.name}")
        
        pol2 = platform.policy_engine.create_policy(
            name="no-public-access",
            policy_type=PolicyType.ACCESS,
            rule='deny { input.public_access == true }',
            scope=["all"],
            enforcement_mode="deny"
        )
        print(f"  ✓ Created: {pol2.name}")
        
        pol3 = platform.policy_engine.create_policy(
            name="require-tags",
            policy_type=PolicyType.DATA,
            rule='deny { not input.tags.owner }',
            scope=["all"],
            enforcement_mode="warn"
        )
        print(f"  ✓ Created: {pol3.name}")
        
        # Проверка ресурсов
        print("\n🔎 Scanning resources...")
        
        resources = [
            {"id": "bucket-1", "type": "s3", "encrypted": True, "public_access": False, "tags": {"owner": "team-a"}},
            {"id": "bucket-2", "type": "s3", "encrypted": False, "public_access": True, "tags": {}},
            {"id": "db-1", "type": "rds", "encrypted": True, "public_access": False, "tags": {"owner": "team-b"}},
            {"id": "vm-1", "type": "ec2", "encrypted": False, "public_access": True, "tags": {}}
        ]
        
        results = await platform.policy_engine.scan_resources(resources)
        violations = [r for r in results if not r["compliant"]]
        print(f"  Resources scanned: {len(resources)}")
        print(f"  Violations found: {len(violations)}")
        
        for v in violations[:3]:
            print(f"    ⚠️ {v['resource_id']}: {v['message']}")
            
        # Remediation
        print("\n🔧 Auto-remediating violations...")
        
        tasks = await platform.remediation_engine.auto_remediate_all()
        completed = len([t for t in tasks if t.status == RemediationStatus.COMPLETED])
        print(f"  Total tasks: {len(tasks)}")
        print(f"  Completed: {completed}")
        
        # Risk assessment
        print("\n⚠️ Risk Assessment...")
        
        assessment = await platform.risk_manager.assess_risk()
        print(f"  Total risks: {assessment.total_risks}")
        print(f"  Critical: {assessment.critical_risks}")
        print(f"  High: {assessment.high_risks}")
        print(f"  Medium: {assessment.medium_risks}")
        print(f"  Risk Score: {assessment.risk_score}")
        
        if assessment.recommendations:
            print("\n  Recommendations:")
            for rec in assessment.recommendations:
                print(f"    → {rec}")
                
        # Compliance report
        print("\n📊 Generating compliance report...")
        
        report = platform.reporter.generate_compliance_report(ComplianceFramework.SOC2)
        print(f"  Framework: {report['framework']}")
        print(f"  Score: {report['summary']['score']}%")
        print(f"  Controls assessed: {report['summary']['assessed']}/{report['summary']['total_controls']}")
        
        # Executive summary
        print("\n📈 Executive Summary:")
        
        summary = platform.reporter.generate_executive_summary()
        print(f"  Frameworks monitored: {summary['overall_compliance']['frameworks_monitored']}")
        print(f"  Average compliance: {summary['overall_compliance']['average_score']}%")
        print(f"  Active violations: {summary['policy_status']['active_violations']}")
        print(f"  Overall risk level: {summary['risk_summary']['overall_risk_level'].upper()}")
        
        # Platform status
        print("\n📊 Platform Status:")
        status = platform.get_status()
        print(f"  Controls: {status['compliance']['controls']}")
        print(f"  Evidence: {status['compliance']['evidence']}")
        print(f"  Policies: {status['policies']['policies']['total']}")
        print(f"  Violations: {status['policies']['violations']['total']}")
        print(f"  Remediations: {status['remediations']['completed']}/{status['remediations']['total']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Compliance & Policy Automation Platform initialized!")
    print("=" * 60)
