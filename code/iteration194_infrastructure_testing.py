#!/usr/bin/env python3
"""
Server Init - Iteration 194: Infrastructure Testing Platform
Платформа тестирования инфраструктуры

Функционал:
- Infrastructure Tests - тесты инфраструктуры
- Policy Compliance - проверка политик
- Security Scanning - сканирование безопасности
- Performance Testing - нагрузочное тестирование
- Chaos Testing - хаос-тестирование
- Drift Detection - обнаружение дрейфа
- Test Automation - автоматизация тестов
- Reports & Analytics - отчёты и аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class TestType(Enum):
    """Тип теста"""
    UNIT = "unit"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CHAOS = "chaos"
    SMOKE = "smoke"
    DRIFT = "drift"


class TestStatus(Enum):
    """Статус теста"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class ResourceType(Enum):
    """Тип ресурса"""
    COMPUTE = "compute"
    NETWORK = "network"
    STORAGE = "storage"
    DATABASE = "database"
    CONTAINER = "container"
    SECURITY_GROUP = "security_group"
    LOAD_BALANCER = "load_balancer"
    DNS = "dns"


class Severity(Enum):
    """Серьёзность"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TestCase:
    """Тестовый случай"""
    test_id: str
    name: str = ""
    description: str = ""
    
    # Type
    test_type: TestType = TestType.UNIT
    
    # Target
    resource_type: Optional[ResourceType] = None
    resource_pattern: str = "*"
    
    # Assertions
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tags
    tags: List[str] = field(default_factory=list)
    
    # Priority
    priority: int = 5  # 1-10, higher = more important
    
    # Status
    is_enabled: bool = True


@dataclass
class TestResult:
    """Результат теста"""
    result_id: str
    test_id: str
    
    # Status
    status: TestStatus = TestStatus.PENDING
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    
    # Output
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Assertions
    assertions_passed: int = 0
    assertions_failed: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    
    # Issues
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestRun:
    """Запуск тестов"""
    run_id: str
    
    # Metadata
    name: str = ""
    triggered_by: str = ""
    trigger_type: str = "manual"  # manual, scheduled, ci
    
    # Tests
    test_ids: List[str] = field(default_factory=list)
    results: Dict[str, List[TestResult]] = field(default_factory=dict)
    
    # Status
    status: TestStatus = TestStatus.PENDING
    
    # Stats
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    @property
    def duration_seconds(self) -> float:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0
        
    @property
    def pass_rate(self) -> float:
        total = self.passed + self.failed
        return (self.passed / total * 100) if total > 0 else 0


@dataclass
class PolicyRule:
    """Правило политики"""
    rule_id: str
    name: str = ""
    description: str = ""
    
    # Target
    resource_types: List[ResourceType] = field(default_factory=list)
    
    # Condition
    condition: str = ""  # Expression to evaluate
    
    # Severity
    severity: Severity = Severity.MEDIUM
    
    # Remediation
    remediation: str = ""
    
    # Status
    is_enabled: bool = True


@dataclass
class ComplianceResult:
    """Результат проверки соответствия"""
    check_id: str
    rule_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Status
    is_compliant: bool = True
    
    # Details
    message: str = ""
    severity: Severity = Severity.MEDIUM
    
    # Remediation
    remediation: str = ""
    
    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class DriftReport:
    """Отчёт о дрейфе"""
    report_id: str
    
    # Resource
    resource_id: str = ""
    resource_name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTE
    
    # Drift
    has_drift: bool = False
    expected_state: Dict[str, Any] = field(default_factory=dict)
    actual_state: Dict[str, Any] = field(default_factory=dict)
    differences: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamp
    detected_at: datetime = field(default_factory=datetime.now)


class TestRegistry:
    """Реестр тестов"""
    
    def __init__(self):
        self.tests: Dict[str, TestCase] = {}
        self.policies: Dict[str, PolicyRule] = {}
        
    def register_test(self, test: TestCase):
        """Регистрация теста"""
        self.tests[test.test_id] = test
        
    def register_policy(self, policy: PolicyRule):
        """Регистрация политики"""
        self.policies[policy.rule_id] = policy
        
    def get_tests_by_type(self, test_type: TestType) -> List[TestCase]:
        """Получение тестов по типу"""
        return [t for t in self.tests.values() if t.test_type == test_type]
        
    def get_tests_by_tag(self, tag: str) -> List[TestCase]:
        """Получение тестов по тегу"""
        return [t for t in self.tests.values() if tag in t.tags]


class TestExecutor:
    """Исполнитель тестов"""
    
    def __init__(self, registry: TestRegistry):
        self.registry = registry
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, test_id: str, handler: Callable):
        """Регистрация обработчика"""
        self.handlers[test_id] = handler
        
    async def execute_test(self, test: TestCase, 
                          resource: Dict[str, Any]) -> TestResult:
        """Выполнение теста"""
        result = TestResult(
            result_id=f"res_{uuid.uuid4().hex[:8]}",
            test_id=test.test_id,
            resource_id=resource.get("id", ""),
            resource_name=resource.get("name", ""),
            started_at=datetime.now()
        )
        
        result.status = TestStatus.RUNNING
        
        try:
            # Get handler
            handler = self.handlers.get(test.test_id)
            
            if handler:
                # Execute custom handler
                passed, message, details = await handler(test, resource)
            else:
                # Default test execution
                passed, message, details = await self._default_execute(test, resource)
                
            result.status = TestStatus.PASSED if passed else TestStatus.FAILED
            result.message = message
            result.details = details
            
            # Count assertions
            for assertion in test.assertions:
                if self._check_assertion(assertion, resource, details):
                    result.assertions_passed += 1
                else:
                    result.assertions_failed += 1
                    result.issues.append({
                        "assertion": assertion,
                        "message": f"Assertion failed: {assertion.get('description', 'No description')}"
                    })
                    
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)
            
        result.completed_at = datetime.now()
        result.duration_ms = (result.completed_at - result.started_at).total_seconds() * 1000
        
        return result
        
    async def _default_execute(self, test: TestCase, 
                              resource: Dict[str, Any]) -> tuple:
        """Стандартное выполнение"""
        await asyncio.sleep(0.01)  # Simulate test
        
        # Simple pass/fail based on random
        passed = random.random() > 0.2
        
        message = "Test passed" if passed else "Test failed"
        details = {
            "resource": resource,
            "checked_at": datetime.now().isoformat()
        }
        
        return passed, message, details
        
    def _check_assertion(self, assertion: Dict[str, Any],
                        resource: Dict[str, Any],
                        details: Dict[str, Any]) -> bool:
        """Проверка утверждения"""
        # Simple assertion check
        field = assertion.get("field")
        expected = assertion.get("expected")
        
        if field and field in resource:
            return resource[field] == expected
            
        return True


class ComplianceChecker:
    """Проверка соответствия"""
    
    def __init__(self, registry: TestRegistry):
        self.registry = registry
        
    def check_resource(self, resource: Dict[str, Any],
                      resource_type: ResourceType) -> List[ComplianceResult]:
        """Проверка ресурса"""
        results = []
        
        for policy in self.registry.policies.values():
            if not policy.is_enabled:
                continue
                
            if policy.resource_types and resource_type not in policy.resource_types:
                continue
                
            result = ComplianceResult(
                check_id=f"check_{uuid.uuid4().hex[:8]}",
                rule_id=policy.rule_id,
                resource_id=resource.get("id", ""),
                resource_name=resource.get("name", ""),
                resource_type=resource_type,
                severity=policy.severity,
                remediation=policy.remediation
            )
            
            # Check compliance (simplified)
            is_compliant = self._evaluate_condition(policy.condition, resource)
            
            result.is_compliant = is_compliant
            result.message = f"Policy '{policy.name}': {'Compliant' if is_compliant else 'Non-compliant'}"
            
            results.append(result)
            
        return results
        
    def _evaluate_condition(self, condition: str, 
                           resource: Dict[str, Any]) -> bool:
        """Вычисление условия"""
        # Simple evaluation
        try:
            return eval(condition, {"__builtins__": {}}, resource)
        except:
            return random.random() > 0.3


class DriftDetector:
    """Детектор дрейфа"""
    
    def __init__(self):
        self.expected_states: Dict[str, Dict[str, Any]] = {}
        
    def set_expected_state(self, resource_id: str, state: Dict[str, Any]):
        """Установка ожидаемого состояния"""
        self.expected_states[resource_id] = state
        
    def detect_drift(self, resource_id: str, 
                    actual_state: Dict[str, Any],
                    resource_type: ResourceType = ResourceType.COMPUTE) -> DriftReport:
        """Обнаружение дрейфа"""
        expected = self.expected_states.get(resource_id, {})
        
        report = DriftReport(
            report_id=f"drift_{uuid.uuid4().hex[:8]}",
            resource_id=resource_id,
            resource_name=actual_state.get("name", ""),
            resource_type=resource_type,
            expected_state=expected,
            actual_state=actual_state
        )
        
        # Compare states
        differences = []
        
        all_keys = set(expected.keys()) | set(actual_state.keys())
        
        for key in all_keys:
            expected_val = expected.get(key)
            actual_val = actual_state.get(key)
            
            if expected_val != actual_val:
                differences.append({
                    "field": key,
                    "expected": expected_val,
                    "actual": actual_val
                })
                
        report.differences = differences
        report.has_drift = len(differences) > 0
        
        return report


class TestRunner:
    """Запускатель тестов"""
    
    def __init__(self, registry: TestRegistry, executor: TestExecutor):
        self.registry = registry
        self.executor = executor
        self.runs: Dict[str, TestRun] = {}
        
    async def run_tests(self, test_ids: List[str] = None,
                       resources: List[Dict[str, Any]] = None,
                       triggered_by: str = "") -> TestRun:
        """Запуск тестов"""
        tests = [self.registry.tests[tid] for tid in test_ids if tid in self.registry.tests] if test_ids else list(self.registry.tests.values())
        resources = resources or [{"id": "default", "name": "default-resource"}]
        
        run = TestRun(
            run_id=f"run_{uuid.uuid4().hex[:8]}",
            name=f"Test Run {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            triggered_by=triggered_by,
            test_ids=[t.test_id for t in tests],
            total_tests=len(tests) * len(resources)
        )
        
        run.status = TestStatus.RUNNING
        
        for test in tests:
            if not test.is_enabled:
                run.skipped += 1
                continue
                
            run.results[test.test_id] = []
            
            for resource in resources:
                result = await self.executor.execute_test(test, resource)
                run.results[test.test_id].append(result)
                
                if result.status == TestStatus.PASSED:
                    run.passed += 1
                elif result.status == TestStatus.FAILED:
                    run.failed += 1
                elif result.status == TestStatus.ERROR:
                    run.errors += 1
                    
        run.status = TestStatus.PASSED if run.failed == 0 and run.errors == 0 else TestStatus.FAILED
        run.completed_at = datetime.now()
        
        self.runs[run.run_id] = run
        return run


class InfrastructureTestingPlatform:
    """Платформа тестирования инфраструктуры"""
    
    def __init__(self):
        self.registry = TestRegistry()
        self.executor = TestExecutor(self.registry)
        self.runner = TestRunner(self.registry, self.executor)
        self.compliance = ComplianceChecker(self.registry)
        self.drift = DriftDetector()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        runs = list(self.runner.runs.values())
        
        total_passed = sum(r.passed for r in runs)
        total_failed = sum(r.failed for r in runs)
        
        return {
            "total_tests": len(self.registry.tests),
            "total_policies": len(self.registry.policies),
            "total_runs": len(runs),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "overall_pass_rate": (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 194: Infrastructure Testing Platform")
    print("=" * 60)
    
    platform = InfrastructureTestingPlatform()
    print("✓ Infrastructure Testing Platform created")
    
    # Register tests
    print("\n📋 Registering Tests...")
    
    tests = [
        TestCase(
            test_id="test_instance_type",
            name="Instance Type Validation",
            description="Verify instance types match expected configuration",
            test_type=TestType.COMPLIANCE,
            resource_type=ResourceType.COMPUTE,
            tags=["compute", "compliance"],
            priority=8
        ),
        TestCase(
            test_id="test_encryption",
            name="Storage Encryption Check",
            description="Verify all storage is encrypted",
            test_type=TestType.SECURITY,
            resource_type=ResourceType.STORAGE,
            tags=["security", "encryption"],
            priority=10
        ),
        TestCase(
            test_id="test_network_rules",
            name="Network Rules Validation",
            description="Verify network security group rules",
            test_type=TestType.SECURITY,
            resource_type=ResourceType.SECURITY_GROUP,
            tags=["security", "network"],
            priority=9
        ),
        TestCase(
            test_id="test_database_backup",
            name="Database Backup Check",
            description="Verify database backup is enabled",
            test_type=TestType.COMPLIANCE,
            resource_type=ResourceType.DATABASE,
            tags=["database", "backup"],
            priority=8
        ),
        TestCase(
            test_id="test_load_balancer_health",
            name="Load Balancer Health Check",
            description="Verify load balancer health check configuration",
            test_type=TestType.INTEGRATION,
            resource_type=ResourceType.LOAD_BALANCER,
            tags=["network", "health"],
            priority=7
        ),
        TestCase(
            test_id="test_container_resources",
            name="Container Resource Limits",
            description="Verify container resource limits are set",
            test_type=TestType.COMPLIANCE,
            resource_type=ResourceType.CONTAINER,
            tags=["container", "resources"],
            priority=6
        ),
        TestCase(
            test_id="test_dns_configuration",
            name="DNS Configuration Check",
            description="Verify DNS records are properly configured",
            test_type=TestType.SMOKE,
            resource_type=ResourceType.DNS,
            tags=["dns", "configuration"],
            priority=5
        ),
        TestCase(
            test_id="test_latency",
            name="Network Latency Test",
            description="Verify network latency is within acceptable limits",
            test_type=TestType.PERFORMANCE,
            resource_type=ResourceType.NETWORK,
            tags=["network", "performance"],
            priority=6
        ),
    ]
    
    for test in tests:
        platform.registry.register_test(test)
        print(f"  ✓ {test.name} ({test.test_type.value})")
        
    # Register policies
    print("\n📜 Registering Policies...")
    
    policies = [
        PolicyRule(
            rule_id="policy_encryption",
            name="Storage Encryption Required",
            description="All storage must be encrypted at rest",
            resource_types=[ResourceType.STORAGE],
            condition="encrypted == True",
            severity=Severity.CRITICAL,
            remediation="Enable encryption on the storage resource"
        ),
        PolicyRule(
            rule_id="policy_public_access",
            name="No Public Access",
            description="Resources should not be publicly accessible",
            resource_types=[ResourceType.STORAGE, ResourceType.DATABASE],
            condition="public_access == False",
            severity=Severity.HIGH,
            remediation="Disable public access and use private endpoints"
        ),
        PolicyRule(
            rule_id="policy_tags",
            name="Required Tags",
            description="Resources must have required tags",
            resource_types=[ResourceType.COMPUTE, ResourceType.STORAGE, ResourceType.DATABASE],
            condition="'environment' in tags and 'owner' in tags",
            severity=Severity.MEDIUM,
            remediation="Add required tags: environment, owner"
        ),
        PolicyRule(
            rule_id="policy_backup",
            name="Backup Enabled",
            description="Databases must have backup enabled",
            resource_types=[ResourceType.DATABASE],
            condition="backup_enabled == True",
            severity=Severity.HIGH,
            remediation="Enable automated backups"
        ),
    ]
    
    for policy in policies:
        platform.registry.register_policy(policy)
        print(f"  ✓ {policy.name} ({policy.severity.value})")
        
    # Create test resources
    print("\n🖥️ Creating Test Resources...")
    
    resources = []
    
    for i in range(15):
        resource = {
            "id": f"resource-{i}",
            "name": f"test-resource-{i}",
            "type": random.choice(list(ResourceType)).value,
            "encrypted": random.random() > 0.2,
            "public_access": random.random() > 0.7,
            "backup_enabled": random.random() > 0.3,
            "tags": {"environment": "production", "owner": "team-a"} if random.random() > 0.3 else {}
        }
        resources.append(resource)
        
        # Set expected state for drift detection
        platform.drift.set_expected_state(resource["id"], resource.copy())
        
    print(f"  Created {len(resources)} test resources")
    
    # Run tests
    print("\n🚀 Running Tests...")
    
    run = await platform.runner.run_tests(
        resources=resources,
        triggered_by="test_user"
    )
    
    print(f"\n  Run ID: {run.run_id}")
    print(f"  Status: {run.status.value}")
    print(f"  Duration: {run.duration_seconds:.2f}s")
    
    # Test results summary
    print("\n📊 Test Results Summary:")
    
    print(f"\n  Total: {run.total_tests}")
    print(f"  Passed: {run.passed} ✅")
    print(f"  Failed: {run.failed} ❌")
    print(f"  Errors: {run.errors} ⚠️")
    print(f"  Skipped: {run.skipped} ⏭️")
    print(f"  Pass Rate: {run.pass_rate:.1f}%")
    
    # Detailed results by test
    print("\n📋 Results by Test:")
    
    print("\n  ┌────────────────────────────────────┬──────────┬────────┬────────┬──────────┐")
    print("  │ Test                               │ Type     │ Passed │ Failed │ Duration │")
    print("  ├────────────────────────────────────┼──────────┼────────┼────────┼──────────┤")
    
    for test_id, results in run.results.items():
        test = platform.registry.tests.get(test_id)
        if not test:
            continue
            
        name = test.name[:34].ljust(34)
        ttype = test.test_type.value[:8].ljust(8)
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        duration = sum(r.duration_ms for r in results)
        
        p = str(passed).rjust(6)
        f = str(failed).rjust(6)
        d = f"{duration:.0f}ms".rjust(8)
        
        print(f"  │ {name} │ {ttype} │ {p} │ {f} │ {d} │")
        
    print("  └────────────────────────────────────┴──────────┴────────┴────────┴──────────┘")
    
    # Compliance check
    print("\n🔒 Compliance Check:")
    
    compliance_results = []
    for resource in resources[:5]:
        rtype = ResourceType(resource["type"]) if resource["type"] in [r.value for r in ResourceType] else ResourceType.COMPUTE
        results = platform.compliance.check_resource(resource, rtype)
        compliance_results.extend(results)
        
    compliant = sum(1 for r in compliance_results if r.is_compliant)
    non_compliant = len(compliance_results) - compliant
    
    print(f"\n  Checked: {len(compliance_results)} policy checks")
    print(f"  Compliant: {compliant} ✅")
    print(f"  Non-compliant: {non_compliant} ❌")
    
    print("\n  Non-compliant Resources:")
    for result in compliance_results:
        if not result.is_compliant:
            policy = platform.registry.policies.get(result.rule_id)
            print(f"    ❌ {result.resource_name}: {policy.name if policy else result.rule_id}")
            print(f"       Severity: {result.severity.value}")
            if result.remediation:
                print(f"       Remediation: {result.remediation}")
                
    # Drift detection
    print("\n🔄 Drift Detection:")
    
    drift_reports = []
    
    for resource in resources[:5]:
        # Simulate drift
        modified = resource.copy()
        if random.random() > 0.6:
            modified["instance_type"] = "t3.large"  # Changed
            modified["tags"] = {}  # Changed
            
        report = platform.drift.detect_drift(
            resource["id"],
            modified,
            ResourceType.COMPUTE
        )
        drift_reports.append(report)
        
    drifted = sum(1 for r in drift_reports if r.has_drift)
    
    print(f"\n  Resources checked: {len(drift_reports)}")
    print(f"  With drift: {drifted}")
    print(f"  No drift: {len(drift_reports) - drifted}")
    
    print("\n  Drift Details:")
    for report in drift_reports:
        if report.has_drift:
            print(f"\n    ⚠️ {report.resource_name}:")
            for diff in report.differences[:3]:
                print(f"       {diff['field']}: {diff['expected']} → {diff['actual']}")
                
    # Test type breakdown
    print("\n📊 Tests by Type:")
    
    by_type = {}
    for test in platform.registry.tests.values():
        t = test.test_type.value
        by_type[t] = by_type.get(t, 0) + 1
        
    for ttype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count + "░" * (10 - count)
        print(f"  {ttype:12} [{bar}] {count}")
        
    # Failed tests detail
    print("\n❌ Failed Tests Details:")
    
    failed_count = 0
    for test_id, results in run.results.items():
        for result in results:
            if result.status == TestStatus.FAILED and failed_count < 5:
                test = platform.registry.tests.get(test_id)
                print(f"\n  {test.name if test else test_id}:")
                print(f"    Resource: {result.resource_name}")
                print(f"    Message: {result.message}")
                for issue in result.issues[:2]:
                    print(f"    Issue: {issue.get('message', '')}")
                failed_count += 1
                
    # Statistics
    stats = platform.get_statistics()
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                 Infrastructure Testing Dashboard                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Test Cases:              {stats['total_tests']:>12}                        │")
    print(f"│ Total Policies:                {stats['total_policies']:>12}                        │")
    print(f"│ Total Test Runs:               {stats['total_runs']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Tests Passed:                  {stats['total_passed']:>12}                        │")
    print(f"│ Tests Failed:                  {stats['total_failed']:>12}                        │")
    print(f"│ Overall Pass Rate:               {stats['overall_pass_rate']:>10.1f}%                   │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Compliance Checks:             {len(compliance_results):>12}                        │")
    print(f"│ Drift Reports:                 {len(drift_reports):>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Infrastructure Testing Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
