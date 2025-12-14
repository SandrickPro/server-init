#!/usr/bin/env python3
"""
Server Init - Iteration 155: Policy as Code Platform
Платформа политик как код

Функционал:
- Policy Definition - определение политик
- Policy Evaluation - оценка политик
- Rego/OPA Integration - интеграция Rego/OPA
- Constraint Templates - шаблоны ограничений
- Violation Reporting - отчёты о нарушениях
- Policy Testing - тестирование политик
- Admission Control - контроль доступа
- Audit Logging - журналирование аудита
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
import re


class PolicyType(Enum):
    """Тип политики"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COST = "cost"
    OPERATIONAL = "operational"
    CUSTOM = "custom"


class PolicyAction(Enum):
    """Действие политики"""
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"
    ALLOW = "allow"


class EvaluationResult(Enum):
    """Результат оценки"""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    ERROR = "error"
    SKIP = "skip"


class ResourceKind(Enum):
    """Тип ресурса"""
    DEPLOYMENT = "Deployment"
    POD = "Pod"
    SERVICE = "Service"
    CONFIGMAP = "ConfigMap"
    SECRET = "Secret"
    INGRESS = "Ingress"
    NAMESPACE = "Namespace"
    SERVICEACCOUNT = "ServiceAccount"


@dataclass
class Policy:
    """Политика"""
    policy_id: str
    name: str = ""
    
    # Type
    policy_type: PolicyType = PolicyType.SECURITY
    
    # Action
    action: PolicyAction = PolicyAction.DENY
    
    # Rules
    rules: List[Dict] = field(default_factory=list)
    
    # Scope
    namespaces: List[str] = field(default_factory=list)
    resource_kinds: List[ResourceKind] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    
    # Status
    enabled: bool = True
    
    # Statistics
    evaluations: int = 0
    violations: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConstraintTemplate:
    """Шаблон ограничения"""
    template_id: str
    name: str = ""
    
    # CRD-like definition
    kind: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Rego code (simplified)
    rego_code: str = ""
    
    # Description
    description: str = ""


@dataclass
class Constraint:
    """Ограничение"""
    constraint_id: str
    name: str = ""
    
    # Template reference
    template_id: str = ""
    
    # Parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Match
    match: Dict = field(default_factory=dict)
    
    # Action
    enforcement_action: PolicyAction = PolicyAction.DENY


@dataclass
class Violation:
    """Нарушение"""
    violation_id: str
    policy_id: str = ""
    
    # Resource
    resource_kind: str = ""
    resource_name: str = ""
    resource_namespace: str = ""
    
    # Details
    message: str = ""
    severity: str = "medium"
    
    # Action taken
    action: PolicyAction = PolicyAction.DENY
    
    # Timestamp
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationReport:
    """Отчёт оценки"""
    report_id: str
    
    # Results
    total_policies: int = 0
    passed: int = 0
    failed: int = 0
    warned: int = 0
    
    # Violations
    violations: List[Violation] = field(default_factory=list)
    
    # Duration
    duration_ms: float = 0.0
    
    # Timestamp
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PolicyTest:
    """Тест политики"""
    test_id: str
    policy_id: str = ""
    
    # Test case
    name: str = ""
    input_resource: Dict = field(default_factory=dict)
    
    # Expected
    expected_result: EvaluationResult = EvaluationResult.PASS
    
    # Actual
    actual_result: Optional[EvaluationResult] = None
    passed: bool = False
    
    # Message
    message: str = ""


@dataclass
class AuditLog:
    """Журнал аудита"""
    log_id: str
    
    # Event
    event_type: str = ""  # evaluate, create, update, delete
    
    # Policy
    policy_id: str = ""
    policy_name: str = ""
    
    # Resource
    resource: Dict = field(default_factory=dict)
    
    # Result
    result: EvaluationResult = EvaluationResult.PASS
    action_taken: PolicyAction = PolicyAction.ALLOW
    
    # Actor
    user: str = ""
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class PolicyEngine:
    """Движок политик"""
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.templates: Dict[str, ConstraintTemplate] = {}
        self.constraints: Dict[str, Constraint] = {}
        
    def create_policy(self, name: str, rules: List[Dict],
                       **kwargs) -> Policy:
        """Создание политики"""
        policy = Policy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=name,
            rules=rules,
            **kwargs
        )
        self.policies[policy.policy_id] = policy
        return policy
        
    def create_template(self, name: str, kind: str,
                         parameters: Dict, rego_code: str,
                         **kwargs) -> ConstraintTemplate:
        """Создание шаблона"""
        template = ConstraintTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            kind=kind,
            parameters=parameters,
            rego_code=rego_code,
            **kwargs
        )
        self.templates[template.template_id] = template
        return template
        
    def create_constraint(self, name: str, template_id: str,
                           parameters: Dict, **kwargs) -> Constraint:
        """Создание ограничения"""
        constraint = Constraint(
            constraint_id=f"con_{uuid.uuid4().hex[:8]}",
            name=name,
            template_id=template_id,
            parameters=parameters,
            **kwargs
        )
        self.constraints[constraint.constraint_id] = constraint
        return constraint
        
    def evaluate(self, resource: Dict) -> EvaluationReport:
        """Оценка ресурса"""
        start_time = datetime.now()
        
        report = EvaluationReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}"
        )
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            # Check scope
            if not self._matches_scope(policy, resource):
                continue
                
            report.total_policies += 1
            policy.evaluations += 1
            
            # Evaluate rules
            result, message = self._evaluate_policy(policy, resource)
            
            if result == EvaluationResult.PASS:
                report.passed += 1
            elif result == EvaluationResult.WARN:
                report.warned += 1
                report.violations.append(self._create_violation(
                    policy, resource, message, PolicyAction.WARN
                ))
            else:
                report.failed += 1
                policy.violations += 1
                report.violations.append(self._create_violation(
                    policy, resource, message, policy.action
                ))
                
        end_time = datetime.now()
        report.duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return report
        
    def _matches_scope(self, policy: Policy, resource: Dict) -> bool:
        """Проверка области применения"""
        kind = resource.get("kind", "")
        namespace = resource.get("metadata", {}).get("namespace", "default")
        
        # Check resource kind
        if policy.resource_kinds:
            if not any(rk.value == kind for rk in policy.resource_kinds):
                return False
                
        # Check namespace
        if policy.namespaces:
            if namespace not in policy.namespaces:
                return False
                
        return True
        
    def _evaluate_policy(self, policy: Policy, resource: Dict) -> tuple:
        """Оценка политики"""
        for rule in policy.rules:
            rule_type = rule.get("type")
            
            if rule_type == "required_labels":
                result, msg = self._check_required_labels(rule, resource)
                if result != EvaluationResult.PASS:
                    return result, msg
                    
            elif rule_type == "forbidden_image":
                result, msg = self._check_forbidden_image(rule, resource)
                if result != EvaluationResult.PASS:
                    return result, msg
                    
            elif rule_type == "resource_limits":
                result, msg = self._check_resource_limits(rule, resource)
                if result != EvaluationResult.PASS:
                    return result, msg
                    
            elif rule_type == "privilege_escalation":
                result, msg = self._check_privilege_escalation(rule, resource)
                if result != EvaluationResult.PASS:
                    return result, msg
                    
            elif rule_type == "host_network":
                result, msg = self._check_host_network(rule, resource)
                if result != EvaluationResult.PASS:
                    return result, msg
                    
        return EvaluationResult.PASS, "All rules passed"
        
    def _check_required_labels(self, rule: Dict, resource: Dict) -> tuple:
        """Проверка обязательных меток"""
        required = rule.get("labels", [])
        labels = resource.get("metadata", {}).get("labels", {})
        
        missing = [l for l in required if l not in labels]
        
        if missing:
            return (
                EvaluationResult.FAIL,
                f"Missing required labels: {', '.join(missing)}"
            )
        return EvaluationResult.PASS, ""
        
    def _check_forbidden_image(self, rule: Dict, resource: Dict) -> tuple:
        """Проверка запрещённых образов"""
        patterns = rule.get("patterns", [])
        
        containers = resource.get("spec", {}).get("template", {}).get(
            "spec", {}).get("containers", [])
            
        for container in containers:
            image = container.get("image", "")
            for pattern in patterns:
                if re.match(pattern, image):
                    return (
                        EvaluationResult.FAIL,
                        f"Forbidden image pattern: {image}"
                    )
        return EvaluationResult.PASS, ""
        
    def _check_resource_limits(self, rule: Dict, resource: Dict) -> tuple:
        """Проверка лимитов ресурсов"""
        containers = resource.get("spec", {}).get("template", {}).get(
            "spec", {}).get("containers", [])
            
        for container in containers:
            resources = container.get("resources", {})
            if not resources.get("limits"):
                return (
                    EvaluationResult.FAIL,
                    f"Container {container.get('name')} missing resource limits"
                )
        return EvaluationResult.PASS, ""
        
    def _check_privilege_escalation(self, rule: Dict, resource: Dict) -> tuple:
        """Проверка эскалации привилегий"""
        containers = resource.get("spec", {}).get("template", {}).get(
            "spec", {}).get("containers", [])
            
        for container in containers:
            sec_context = container.get("securityContext", {})
            if sec_context.get("allowPrivilegeEscalation", False):
                return (
                    EvaluationResult.FAIL,
                    f"Container {container.get('name')} allows privilege escalation"
                )
        return EvaluationResult.PASS, ""
        
    def _check_host_network(self, rule: Dict, resource: Dict) -> tuple:
        """Проверка host network"""
        spec = resource.get("spec", {}).get("template", {}).get("spec", {})
        
        if spec.get("hostNetwork", False):
            return (
                EvaluationResult.FAIL,
                "Pod uses host network"
            )
        return EvaluationResult.PASS, ""
        
    def _create_violation(self, policy: Policy, resource: Dict,
                           message: str, action: PolicyAction) -> Violation:
        """Создание нарушения"""
        return Violation(
            violation_id=f"vio_{uuid.uuid4().hex[:8]}",
            policy_id=policy.policy_id,
            resource_kind=resource.get("kind", ""),
            resource_name=resource.get("metadata", {}).get("name", ""),
            resource_namespace=resource.get("metadata", {}).get("namespace", "default"),
            message=message,
            severity=policy.severity,
            action=action
        )


class PolicyTester:
    """Тестер политик"""
    
    def __init__(self, engine: PolicyEngine):
        self.engine = engine
        self.tests: Dict[str, List[PolicyTest]] = {}
        
    def add_test(self, policy_id: str, name: str, input_resource: Dict,
                  expected_result: EvaluationResult) -> PolicyTest:
        """Добавление теста"""
        test = PolicyTest(
            test_id=f"test_{uuid.uuid4().hex[:8]}",
            policy_id=policy_id,
            name=name,
            input_resource=input_resource,
            expected_result=expected_result
        )
        
        if policy_id not in self.tests:
            self.tests[policy_id] = []
        self.tests[policy_id].append(test)
        
        return test
        
    def run_tests(self, policy_id: str = None) -> Dict:
        """Запуск тестов"""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        policies = [policy_id] if policy_id else list(self.tests.keys())
        
        for pid in policies:
            if pid not in self.tests:
                continue
                
            for test in self.tests[pid]:
                results["total"] += 1
                
                # Run evaluation
                report = self.engine.evaluate(test.input_resource)
                
                # Determine actual result
                if report.failed > 0:
                    test.actual_result = EvaluationResult.FAIL
                elif report.warned > 0:
                    test.actual_result = EvaluationResult.WARN
                else:
                    test.actual_result = EvaluationResult.PASS
                    
                # Check expectation
                test.passed = (test.actual_result == test.expected_result)
                
                if test.passed:
                    results["passed"] += 1
                    test.message = "Test passed"
                else:
                    results["failed"] += 1
                    test.message = f"Expected {test.expected_result.value}, got {test.actual_result.value}"
                    
                results["details"].append({
                    "test_id": test.test_id,
                    "name": test.name,
                    "passed": test.passed,
                    "message": test.message
                })
                
        return results


class AuditLogger:
    """Журнал аудита"""
    
    def __init__(self):
        self.logs: List[AuditLog] = []
        
    def log(self, event_type: str, policy_id: str, policy_name: str,
             resource: Dict, result: EvaluationResult,
             action: PolicyAction, user: str = "") -> AuditLog:
        """Запись в журнал"""
        log = AuditLog(
            log_id=f"log_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            policy_id=policy_id,
            policy_name=policy_name,
            resource=resource,
            result=result,
            action_taken=action,
            user=user
        )
        self.logs.append(log)
        return log
        
    def get_logs(self, policy_id: str = None,
                  start_time: datetime = None,
                  end_time: datetime = None) -> List[AuditLog]:
        """Получение логов"""
        results = self.logs
        
        if policy_id:
            results = [l for l in results if l.policy_id == policy_id]
            
        if start_time:
            results = [l for l in results if l.timestamp >= start_time]
            
        if end_time:
            results = [l for l in results if l.timestamp <= end_time]
            
        return results


class AdmissionController:
    """Контроллер доступа"""
    
    def __init__(self, engine: PolicyEngine, audit: AuditLogger):
        self.engine = engine
        self.audit = audit
        
    async def admit(self, request: Dict) -> Dict:
        """Обработка запроса на допуск"""
        resource = request.get("object", {})
        user = request.get("userInfo", {}).get("username", "")
        
        # Evaluate policies
        report = self.engine.evaluate(resource)
        
        # Determine admission
        allowed = report.failed == 0
        
        # Log audit
        for policy in self.engine.policies.values():
            result = EvaluationResult.PASS if allowed else EvaluationResult.FAIL
            self.audit.log(
                "evaluate",
                policy.policy_id,
                policy.name,
                resource,
                result,
                PolicyAction.ALLOW if allowed else PolicyAction.DENY,
                user
            )
            
        response = {
            "allowed": allowed,
            "status": {
                "code": 200 if allowed else 403,
                "message": "Allowed" if allowed else "Denied by policy"
            }
        }
        
        if not allowed and report.violations:
            response["status"]["message"] = report.violations[0].message
            
        return response


class PolicyAsCodePlatform:
    """Платформа политик как код"""
    
    def __init__(self):
        self.engine = PolicyEngine()
        self.tester = PolicyTester(self.engine)
        self.audit = AuditLogger()
        self.admission = AdmissionController(self.engine, self.audit)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        policies = list(self.engine.policies.values())
        
        total_evaluations = sum(p.evaluations for p in policies)
        total_violations = sum(p.violations for p in policies)
        
        return {
            "total_policies": len(policies),
            "enabled_policies": len([p for p in policies if p.enabled]),
            "templates": len(self.engine.templates),
            "constraints": len(self.engine.constraints),
            "total_evaluations": total_evaluations,
            "total_violations": total_violations,
            "audit_logs": len(self.audit.logs),
            "violation_rate": (total_violations / total_evaluations * 100) if total_evaluations > 0 else 0
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 155: Policy as Code Platform")
    print("=" * 60)
    
    async def demo():
        platform = PolicyAsCodePlatform()
        print("✓ Policy as Code Platform created")
        
        # Create policies
        print("\n📋 Creating Policies...")
        
        # Required labels policy
        labels_policy = platform.engine.create_policy(
            name="require-labels",
            rules=[
                {"type": "required_labels", "labels": ["app", "env", "owner"]}
            ],
            policy_type=PolicyType.COMPLIANCE,
            action=PolicyAction.DENY,
            severity="high",
            description="Require standard labels on all resources"
        )
        print(f"  ✓ {labels_policy.name}: {labels_policy.policy_type.value}")
        
        # Resource limits policy
        limits_policy = platform.engine.create_policy(
            name="require-resource-limits",
            rules=[
                {"type": "resource_limits"}
            ],
            policy_type=PolicyType.OPERATIONAL,
            action=PolicyAction.DENY,
            severity="high",
            resource_kinds=[ResourceKind.DEPLOYMENT],
            description="Require resource limits on containers"
        )
        print(f"  ✓ {limits_policy.name}: {limits_policy.policy_type.value}")
        
        # Security policies
        security_policy = platform.engine.create_policy(
            name="no-privilege-escalation",
            rules=[
                {"type": "privilege_escalation"}
            ],
            policy_type=PolicyType.SECURITY,
            action=PolicyAction.DENY,
            severity="critical",
            description="Prevent privilege escalation in containers"
        )
        print(f"  ✓ {security_policy.name}: {security_policy.policy_type.value}")
        
        host_network_policy = platform.engine.create_policy(
            name="no-host-network",
            rules=[
                {"type": "host_network"}
            ],
            policy_type=PolicyType.SECURITY,
            action=PolicyAction.WARN,
            severity="medium",
            description="Warn on host network usage"
        )
        print(f"  ✓ {host_network_policy.name}: {host_network_policy.policy_type.value}")
        
        # Forbidden images policy
        images_policy = platform.engine.create_policy(
            name="allowed-registries",
            rules=[
                {"type": "forbidden_image", "patterns": [r"^(?!gcr\.io|docker\.io).*"]}
            ],
            policy_type=PolicyType.SECURITY,
            action=PolicyAction.DENY,
            severity="high",
            description="Only allow images from approved registries"
        )
        print(f"  ✓ {images_policy.name}: {images_policy.policy_type.value}")
        
        # Create constraint templates
        print("\n📝 Creating Constraint Templates...")
        
        template = platform.engine.create_template(
            name="K8sRequiredLabels",
            kind="K8sRequiredLabels",
            parameters={"labels": {"type": "array", "items": {"type": "string"}}},
            rego_code="""
                package k8srequiredlabels
                violation[{"msg": msg}] {
                    provided := {label | input.review.object.metadata.labels[label]}
                    required := {label | label := input.parameters.labels[_]}
                    missing := required - provided
                    count(missing) > 0
                    msg := sprintf("Missing labels: %v", [missing])
                }
            """,
            description="Requires resources to have specified labels"
        )
        print(f"  ✓ {template.name}")
        
        # Test resources
        print("\n🧪 Evaluating Resources...")
        
        # Compliant deployment
        compliant_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "web-app",
                "namespace": "production",
                "labels": {
                    "app": "web",
                    "env": "production",
                    "owner": "platform-team"
                }
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "web",
                            "image": "gcr.io/project/web:v1",
                            "resources": {
                                "limits": {"cpu": "500m", "memory": "512Mi"},
                                "requests": {"cpu": "250m", "memory": "256Mi"}
                            },
                            "securityContext": {
                                "allowPrivilegeEscalation": False
                            }
                        }]
                    }
                }
            }
        }
        
        report1 = platform.engine.evaluate(compliant_deployment)
        print(f"\n  Compliant Deployment:")
        print(f"    Policies evaluated: {report1.total_policies}")
        print(f"    Passed: {report1.passed}")
        print(f"    Failed: {report1.failed}")
        print(f"    Warnings: {report1.warned}")
        
        # Non-compliant deployment
        non_compliant_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "risky-app",
                "namespace": "default",
                "labels": {
                    "app": "risky"
                }
            },
            "spec": {
                "template": {
                    "spec": {
                        "hostNetwork": True,
                        "containers": [{
                            "name": "risky",
                            "image": "docker.io/library/nginx:latest",
                            "securityContext": {
                                "allowPrivilegeEscalation": True
                            }
                        }]
                    }
                }
            }
        }
        
        report2 = platform.engine.evaluate(non_compliant_deployment)
        print(f"\n  Non-Compliant Deployment:")
        print(f"    Policies evaluated: {report2.total_policies}")
        print(f"    Passed: {report2.passed}")
        print(f"    Failed: {report2.failed}")
        print(f"    Warnings: {report2.warned}")
        
        if report2.violations:
            print(f"\n    Violations:")
            for v in report2.violations:
                severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                icon = severity_icon.get(v.severity, "⚪")
                print(f"      {icon} {v.message}")
                
        # Add tests
        print("\n🧪 Policy Testing...")
        
        platform.tester.add_test(
            labels_policy.policy_id,
            "Should pass with all required labels",
            compliant_deployment,
            EvaluationResult.PASS
        )
        
        platform.tester.add_test(
            labels_policy.policy_id,
            "Should fail without required labels",
            non_compliant_deployment,
            EvaluationResult.FAIL
        )
        
        platform.tester.add_test(
            security_policy.policy_id,
            "Should fail with privilege escalation",
            non_compliant_deployment,
            EvaluationResult.FAIL
        )
        
        test_results = platform.tester.run_tests()
        
        print(f"\n  Test Results:")
        print(f"    Total: {test_results['total']}")
        print(f"    Passed: {test_results['passed']}")
        print(f"    Failed: {test_results['failed']}")
        
        for detail in test_results["details"]:
            status = "✓" if detail["passed"] else "✗"
            print(f"      {status} {detail['name']}")
            
        # Admission control
        print("\n🚪 Admission Control...")
        
        admission_request = {
            "object": non_compliant_deployment,
            "userInfo": {"username": "developer@company.com"}
        }
        
        response = await platform.admission.admit(admission_request)
        
        print(f"\n  Request: Create {non_compliant_deployment['metadata']['name']}")
        print(f"  User: developer@company.com")
        print(f"  Allowed: {response['allowed']}")
        print(f"  Message: {response['status']['message']}")
        
        # Policy summary
        print("\n📊 Policy Summary:")
        print("  ┌─────────────────────────────────────────────────────────────────────────┐")
        print("  │ Policy                    │ Type       │ Severity │ Evals │ Violations │")
        print("  ├─────────────────────────────────────────────────────────────────────────┤")
        
        for policy in platform.engine.policies.values():
            name = policy.name[:25].ljust(25)
            ptype = policy.policy_type.value[:10].ljust(10)
            sev = policy.severity[:8].ljust(8)
            print(f"  │ {name} │ {ptype} │ {sev} │ {policy.evaluations:5} │ {policy.violations:10} │")
            
        print("  └─────────────────────────────────────────────────────────────────────────┘")
        
        # Audit logs
        print("\n📜 Recent Audit Logs:")
        
        for log in platform.audit.logs[-5:]:
            result_icon = "✓" if log.result == EvaluationResult.PASS else "✗"
            print(f"  {result_icon} {log.event_type}: {log.policy_name} → {log.action_taken.value}")
            
        # Statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Policies: {stats['total_policies']}")
        print(f"  Enabled: {stats['enabled_policies']}")
        print(f"  Templates: {stats['templates']}")
        print(f"  Total Evaluations: {stats['total_evaluations']}")
        print(f"  Total Violations: {stats['total_violations']}")
        print(f"  Violation Rate: {stats['violation_rate']:.1f}%")
        print(f"  Audit Logs: {stats['audit_logs']}")
        
        # Dashboard
        print("\n📋 Policy as Code Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │                  Policy as Code Overview                   │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Policies:          {stats['total_policies']:>10}                    │")
        print(f"  │ Enabled:                 {stats['enabled_policies']:>10}                    │")
        print(f"  │ Templates:               {stats['templates']:>10}                    │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Evaluations:       {stats['total_evaluations']:>10}                    │")
        print(f"  │ Total Violations:        {stats['total_violations']:>10}                    │")
        print(f"  │ Violation Rate:          {stats['violation_rate']:>10.1f}%                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Policy as Code Platform initialized!")
    print("=" * 60)
