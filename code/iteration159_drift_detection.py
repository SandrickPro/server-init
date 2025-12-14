#!/usr/bin/env python3
"""
Server Init - Iteration 159: Infrastructure Drift Detection Platform
Платформа обнаружения дрифта инфраструктуры

Функционал:
- State Comparison - сравнение состояний
- Drift Detection - обнаружение дрифта
- Resource Tracking - отслеживание ресурсов
- Change Analysis - анализ изменений
- Remediation Suggestions - рекомендации по исправлению
- Historical Drift - история дрифта
- Alert Management - управление алертами
- Drift Reporting - отчёты о дрифте
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid
import hashlib
from copy import deepcopy


class DriftType(Enum):
    """Тип дрифта"""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class DriftSeverity(Enum):
    """Серьёзность дрифта"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceStatus(Enum):
    """Статус ресурса"""
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    DRIFTED = "drifted"
    DELETED = "deleted"


class RemediationAction(Enum):
    """Действие по исправлению"""
    UPDATE_STATE = "update_state"
    UPDATE_RESOURCE = "update_resource"
    DELETE_RESOURCE = "delete_resource"
    CREATE_RESOURCE = "create_resource"
    IGNORE = "ignore"


class AlertStatus(Enum):
    """Статус алерта"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class ResourceAttribute:
    """Атрибут ресурса"""
    name: str
    expected_value: Any = None
    actual_value: Any = None
    drift_type: DriftType = DriftType.UNCHANGED


@dataclass
class Resource:
    """Ресурс инфраструктуры"""
    resource_id: str
    resource_type: str = ""
    name: str = ""
    
    # Provider
    provider: str = ""  # aws, azure, gcp, kubernetes
    
    # State
    expected_state: Dict = field(default_factory=dict)
    actual_state: Dict = field(default_factory=dict)
    
    # Status
    status: ResourceStatus = ResourceStatus.MANAGED
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    region: str = ""
    
    # Drift
    drifted: bool = False
    drift_attributes: List[ResourceAttribute] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None
    last_drift_detected: Optional[datetime] = None


@dataclass
class DriftChange:
    """Изменение дрифта"""
    change_id: str
    resource_id: str = ""
    
    # Attribute
    attribute_path: str = ""
    
    # Values
    expected_value: Any = None
    actual_value: Any = None
    
    # Type
    drift_type: DriftType = DriftType.MODIFIED
    severity: DriftSeverity = DriftSeverity.MEDIUM
    
    # Timestamp
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class DriftReport:
    """Отчёт о дрифте"""
    report_id: str
    
    # Scope
    resources_checked: int = 0
    resources_drifted: int = 0
    
    # Changes
    changes: List[DriftChange] = field(default_factory=list)
    
    # Summary by severity
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Summary by type
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0
    
    # Duration
    duration_seconds: float = 0.0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Remediation:
    """Исправление"""
    remediation_id: str
    change_id: str = ""
    resource_id: str = ""
    
    # Action
    action: RemediationAction = RemediationAction.UPDATE_RESOURCE
    
    # Details
    description: str = ""
    commands: List[str] = field(default_factory=list)
    
    # Risk
    risk_level: str = "medium"  # low, medium, high
    
    # Auto-remediation
    auto_apply: bool = False
    applied: bool = False
    
    # Result
    success: bool = False
    error: str = ""


@dataclass
class DriftAlert:
    """Алерт дрифта"""
    alert_id: str
    
    # Resource
    resource_id: str = ""
    resource_type: str = ""
    resource_name: str = ""
    
    # Drift
    drift_type: DriftType = DriftType.MODIFIED
    severity: DriftSeverity = DriftSeverity.MEDIUM
    
    # Status
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Message
    message: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class DriftPolicy:
    """Политика дрифта"""
    policy_id: str
    name: str = ""
    
    # Scope
    resource_types: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Ignored attributes
    ignored_attributes: List[str] = field(default_factory=list)
    
    # Severity mapping
    severity_overrides: Dict[str, DriftSeverity] = field(default_factory=dict)
    
    # Actions
    auto_remediate: bool = False
    alert_on_drift: bool = True
    
    # Enabled
    enabled: bool = True


@dataclass
class StateSnapshot:
    """Снимок состояния"""
    snapshot_id: str
    
    # Resources
    resources: Dict[str, Dict] = field(default_factory=dict)
    
    # Metadata
    source: str = ""  # terraform, cloudformation, pulumi
    version: str = ""
    
    # Timestamp
    captured_at: datetime = field(default_factory=datetime.now)


class StateManager:
    """Менеджер состояния"""
    
    def __init__(self):
        self.expected_states: Dict[str, StateSnapshot] = {}
        self.actual_states: Dict[str, StateSnapshot] = {}
        
    def save_expected_state(self, source: str, resources: Dict) -> StateSnapshot:
        """Сохранение ожидаемого состояния"""
        snapshot = StateSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            resources=resources,
            source=source
        )
        self.expected_states[source] = snapshot
        return snapshot
        
    def save_actual_state(self, source: str, resources: Dict) -> StateSnapshot:
        """Сохранение актуального состояния"""
        snapshot = StateSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            resources=resources,
            source=source
        )
        self.actual_states[source] = snapshot
        return snapshot
        
    def get_resource_hash(self, resource_state: Dict) -> str:
        """Получение хеша ресурса"""
        return hashlib.sha256(
            json.dumps(resource_state, sort_keys=True).encode()
        ).hexdigest()[:16]


class DriftDetector:
    """Детектор дрифта"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.policies: Dict[str, DriftPolicy] = {}
        
    def add_policy(self, policy: DriftPolicy):
        """Добавление политики"""
        self.policies[policy.policy_id] = policy
        
    def detect(self, expected: Dict, actual: Dict,
                resource_type: str = "") -> List[DriftChange]:
        """Обнаружение дрифта"""
        changes = []
        
        # Get applicable policy
        policy = self._get_policy(resource_type)
        ignored = policy.ignored_attributes if policy else []
        
        # Compare
        self._compare_dicts(
            expected, actual, "", changes, ignored, resource_type
        )
        
        return changes
        
    def _get_policy(self, resource_type: str) -> Optional[DriftPolicy]:
        """Получение политики"""
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            if not policy.resource_types or resource_type in policy.resource_types:
                return policy
        return None
        
    def _compare_dicts(self, expected: Dict, actual: Dict, path: str,
                        changes: List, ignored: List, resource_type: str):
        """Сравнение словарей"""
        all_keys = set(expected.keys()) | set(actual.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            # Skip ignored
            if current_path in ignored:
                continue
                
            exp_val = expected.get(key)
            act_val = actual.get(key)
            
            if key not in expected:
                # Added in actual
                changes.append(self._create_change(
                    current_path, None, act_val, 
                    DriftType.ADDED, resource_type
                ))
            elif key not in actual:
                # Removed from actual
                changes.append(self._create_change(
                    current_path, exp_val, None,
                    DriftType.REMOVED, resource_type
                ))
            elif isinstance(exp_val, dict) and isinstance(act_val, dict):
                # Recurse
                self._compare_dicts(
                    exp_val, act_val, current_path,
                    changes, ignored, resource_type
                )
            elif exp_val != act_val:
                # Modified
                changes.append(self._create_change(
                    current_path, exp_val, act_val,
                    DriftType.MODIFIED, resource_type
                ))
                
    def _create_change(self, path: str, expected: Any, actual: Any,
                        drift_type: DriftType, resource_type: str) -> DriftChange:
        """Создание изменения"""
        # Determine severity
        severity = self._determine_severity(path, drift_type, resource_type)
        
        return DriftChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            attribute_path=path,
            expected_value=expected,
            actual_value=actual,
            drift_type=drift_type,
            severity=severity
        )
        
    def _determine_severity(self, path: str, drift_type: DriftType,
                             resource_type: str) -> DriftSeverity:
        """Определение серьёзности"""
        # Security-related attributes
        security_attrs = [
            "security_groups", "iam_role", "encryption",
            "public_access", "network_acls", "firewall_rules",
            "secrets", "passwords", "keys"
        ]
        
        # Check if security-related
        for attr in security_attrs:
            if attr in path.lower():
                return DriftSeverity.CRITICAL
                
        # Resource type based
        critical_types = ["aws_iam_role", "aws_security_group", "aws_kms_key"]
        if resource_type in critical_types:
            return DriftSeverity.HIGH
            
        # Default by drift type
        if drift_type == DriftType.REMOVED:
            return DriftSeverity.HIGH
        elif drift_type == DriftType.ADDED:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW


class ResourceTracker:
    """Трекер ресурсов"""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.history: List[Dict] = []
        
    def track(self, resource_type: str, name: str, provider: str,
               expected_state: Dict, actual_state: Dict = None) -> Resource:
        """Отслеживание ресурса"""
        resource_id = f"{provider}_{resource_type}_{name}"
        
        resource = Resource(
            resource_id=resource_id,
            resource_type=resource_type,
            name=name,
            provider=provider,
            expected_state=expected_state,
            actual_state=actual_state or expected_state
        )
        
        self.resources[resource_id] = resource
        return resource
        
    def update_actual_state(self, resource_id: str, actual_state: Dict):
        """Обновление актуального состояния"""
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            
            # Save to history
            self.history.append({
                "resource_id": resource_id,
                "previous_state": deepcopy(resource.actual_state),
                "new_state": actual_state,
                "timestamp": datetime.now().isoformat()
            })
            
            resource.actual_state = actual_state
            resource.last_checked = datetime.now()
            
    def mark_drifted(self, resource_id: str, drift_attributes: List[ResourceAttribute]):
        """Пометка как дрифтовый"""
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            resource.drifted = True
            resource.status = ResourceStatus.DRIFTED
            resource.drift_attributes = drift_attributes
            resource.last_drift_detected = datetime.now()
            
    def mark_compliant(self, resource_id: str):
        """Пометка как соответствующий"""
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            resource.drifted = False
            resource.status = ResourceStatus.MANAGED
            resource.drift_attributes = []


class RemediationEngine:
    """Движок исправлений"""
    
    def __init__(self, tracker: ResourceTracker):
        self.tracker = tracker
        self.remediations: Dict[str, Remediation] = {}
        
    def suggest(self, resource: Resource, change: DriftChange) -> Remediation:
        """Предложение исправления"""
        action = self._determine_action(change)
        commands = self._generate_commands(resource, change, action)
        
        remediation = Remediation(
            remediation_id=f"rem_{uuid.uuid4().hex[:8]}",
            change_id=change.change_id,
            resource_id=resource.resource_id,
            action=action,
            description=self._generate_description(resource, change, action),
            commands=commands,
            risk_level=self._assess_risk(change)
        )
        
        self.remediations[remediation.remediation_id] = remediation
        return remediation
        
    def _determine_action(self, change: DriftChange) -> RemediationAction:
        """Определение действия"""
        if change.drift_type == DriftType.ADDED:
            return RemediationAction.DELETE_RESOURCE
        elif change.drift_type == DriftType.REMOVED:
            return RemediationAction.CREATE_RESOURCE
        else:
            return RemediationAction.UPDATE_RESOURCE
            
    def _generate_commands(self, resource: Resource, change: DriftChange,
                            action: RemediationAction) -> List[str]:
        """Генерация команд"""
        commands = []
        
        if resource.provider == "aws":
            if action == RemediationAction.UPDATE_RESOURCE:
                commands.append(f"aws {resource.resource_type} update ...")
            elif action == RemediationAction.DELETE_RESOURCE:
                commands.append(f"aws {resource.resource_type} delete --name {resource.name}")
                
        elif resource.provider == "terraform":
            commands.append(f"terraform plan -target={resource.resource_type}.{resource.name}")
            commands.append(f"terraform apply -target={resource.resource_type}.{resource.name}")
            
        return commands
        
    def _generate_description(self, resource: Resource, change: DriftChange,
                               action: RemediationAction) -> str:
        """Генерация описания"""
        return (f"{action.value}: {resource.resource_type}/{resource.name} - "
                f"attribute '{change.attribute_path}' "
                f"expected '{change.expected_value}' but got '{change.actual_value}'")
                
    def _assess_risk(self, change: DriftChange) -> str:
        """Оценка риска"""
        if change.severity == DriftSeverity.CRITICAL:
            return "high"
        elif change.severity == DriftSeverity.HIGH:
            return "medium"
        else:
            return "low"
            
    async def apply(self, remediation: Remediation) -> bool:
        """Применение исправления"""
        try:
            # Simulate applying remediation
            await asyncio.sleep(0.1)
            
            remediation.applied = True
            remediation.success = True
            
            # Update resource
            resource = self.tracker.resources.get(remediation.resource_id)
            if resource:
                self.tracker.mark_compliant(remediation.resource_id)
                
            return True
            
        except Exception as e:
            remediation.error = str(e)
            remediation.success = False
            return False


class AlertManager:
    """Менеджер алертов"""
    
    def __init__(self):
        self.alerts: Dict[str, DriftAlert] = {}
        
    def create_alert(self, resource: Resource, change: DriftChange) -> DriftAlert:
        """Создание алерта"""
        alert = DriftAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            resource_name=resource.name,
            drift_type=change.drift_type,
            severity=change.severity,
            message=f"Drift detected in {resource.resource_type}/{resource.name}: "
                    f"{change.attribute_path} changed"
        )
        
        self.alerts[alert.alert_id] = alert
        return alert
        
    def acknowledge(self, alert_id: str, user: str = "") -> bool:
        """Подтверждение алерта"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            return True
        return False
        
    def resolve(self, alert_id: str) -> bool:
        """Закрытие алерта"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            return True
        return False
        
    def get_active_alerts(self) -> List[DriftAlert]:
        """Получение активных алертов"""
        return [
            a for a in self.alerts.values()
            if a.status == AlertStatus.ACTIVE
        ]


class DriftReporter:
    """Генератор отчётов"""
    
    def __init__(self):
        self.reports: List[DriftReport] = []
        
    def generate_report(self, resources: List[Resource],
                         changes: List[DriftChange]) -> DriftReport:
        """Генерация отчёта"""
        report = DriftReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            resources_checked=len(resources),
            resources_drifted=len([r for r in resources if r.drifted]),
            changes=changes
        )
        
        # Count by severity
        for change in changes:
            if change.severity == DriftSeverity.CRITICAL:
                report.critical_count += 1
            elif change.severity == DriftSeverity.HIGH:
                report.high_count += 1
            elif change.severity == DriftSeverity.MEDIUM:
                report.medium_count += 1
            else:
                report.low_count += 1
                
        # Count by type
        for change in changes:
            if change.drift_type == DriftType.ADDED:
                report.added_count += 1
            elif change.drift_type == DriftType.REMOVED:
                report.removed_count += 1
            elif change.drift_type == DriftType.MODIFIED:
                report.modified_count += 1
                
        report.completed_at = datetime.now()
        report.duration_seconds = (
            report.completed_at - report.started_at
        ).total_seconds()
        
        self.reports.append(report)
        return report


class InfrastructureDriftPlatform:
    """Платформа обнаружения дрифта"""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.detector = DriftDetector(self.state_manager)
        self.tracker = ResourceTracker()
        self.remediation = RemediationEngine(self.tracker)
        self.alerts = AlertManager()
        self.reporter = DriftReporter()
        
    async def detect_drift(self) -> DriftReport:
        """Обнаружение дрифта"""
        all_changes = []
        
        for resource in self.tracker.resources.values():
            changes = self.detector.detect(
                resource.expected_state,
                resource.actual_state,
                resource.resource_type
            )
            
            if changes:
                # Mark as drifted
                drift_attrs = [
                    ResourceAttribute(
                        name=c.attribute_path,
                        expected_value=c.expected_value,
                        actual_value=c.actual_value,
                        drift_type=c.drift_type
                    )
                    for c in changes
                ]
                
                self.tracker.mark_drifted(resource.resource_id, drift_attrs)
                
                # Set resource_id on changes
                for change in changes:
                    change.resource_id = resource.resource_id
                    
                # Create alerts
                for change in changes:
                    self.alerts.create_alert(resource, change)
                    
                all_changes.extend(changes)
            else:
                self.tracker.mark_compliant(resource.resource_id)
                
        # Generate report
        report = self.reporter.generate_report(
            list(self.tracker.resources.values()),
            all_changes
        )
        
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        resources = list(self.tracker.resources.values())
        alerts = list(self.alerts.alerts.values())
        
        return {
            "total_resources": len(resources),
            "drifted_resources": len([r for r in resources if r.drifted]),
            "compliant_resources": len([r for r in resources if not r.drifted]),
            "total_alerts": len(alerts),
            "active_alerts": len([a for a in alerts if a.status == AlertStatus.ACTIVE]),
            "remediations": len(self.remediation.remediations),
            "reports": len(self.reporter.reports)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 159: Infrastructure Drift Detection")
    print("=" * 60)
    
    async def demo():
        platform = InfrastructureDriftPlatform()
        print("✓ Infrastructure Drift Detection Platform created")
        
        # Add drift policy
        print("\n📋 Adding Drift Policies...")
        
        policy = DriftPolicy(
            policy_id="default",
            name="Default Drift Policy",
            resource_types=["aws_instance", "aws_security_group", "aws_s3_bucket"],
            ignored_attributes=["last_modified", "etag", "version_id"],
            auto_remediate=False,
            alert_on_drift=True
        )
        platform.detector.add_policy(policy)
        print(f"  ✓ {policy.name}")
        
        # Track resources
        print("\n📦 Tracking Resources...")
        
        # EC2 Instance - will have drift
        ec2_expected = {
            "instance_type": "t3.medium",
            "ami": "ami-12345678",
            "security_groups": ["sg-web", "sg-default"],
            "tags": {"Name": "web-server", "Environment": "production"},
            "monitoring": {"enabled": True},
            "root_block_device": {"volume_size": 50, "encrypted": True}
        }
        
        ec2_actual = {
            "instance_type": "t3.large",  # Drifted
            "ami": "ami-12345678",
            "security_groups": ["sg-web", "sg-default", "sg-extra"],  # Added
            "tags": {"Name": "web-server", "Environment": "staging"},  # Changed
            "monitoring": {"enabled": True},
            "root_block_device": {"volume_size": 50, "encrypted": True}
        }
        
        ec2 = platform.tracker.track(
            "aws_instance", "web-server", "aws",
            ec2_expected, ec2_actual
        )
        print(f"  ✓ {ec2.resource_type}/{ec2.name}")
        
        # Security Group - will have drift
        sg_expected = {
            "name": "web-sg",
            "description": "Web security group",
            "ingress": [
                {"from_port": 443, "to_port": 443, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]},
                {"from_port": 80, "to_port": 80, "protocol": "tcp", "cidr_blocks": ["10.0.0.0/8"]}
            ],
            "egress": [
                {"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}
            ]
        }
        
        sg_actual = {
            "name": "web-sg",
            "description": "Web security group",
            "ingress": [
                {"from_port": 443, "to_port": 443, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]},
                {"from_port": 80, "to_port": 80, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]},  # Changed
                {"from_port": 22, "to_port": 22, "protocol": "tcp", "cidr_blocks": ["0.0.0.0/0"]}  # Added - Critical!
            ],
            "egress": [
                {"from_port": 0, "to_port": 0, "protocol": "-1", "cidr_blocks": ["0.0.0.0/0"]}
            ]
        }
        
        sg = platform.tracker.track(
            "aws_security_group", "web-sg", "aws",
            sg_expected, sg_actual
        )
        print(f"  ✓ {sg.resource_type}/{sg.name}")
        
        # S3 Bucket - no drift
        s3_expected = {
            "bucket": "my-app-data",
            "acl": "private",
            "versioning": {"enabled": True},
            "encryption": {"sse_algorithm": "aws:kms"}
        }
        
        s3 = platform.tracker.track(
            "aws_s3_bucket", "my-app-data", "aws",
            s3_expected, s3_expected  # Same - no drift
        )
        print(f"  ✓ {s3.resource_type}/{s3.name}")
        
        # RDS Instance - will have drift
        rds_expected = {
            "identifier": "app-db",
            "instance_class": "db.t3.medium",
            "engine": "postgres",
            "engine_version": "13.4",
            "storage_encrypted": True,
            "backup_retention_period": 7,
            "multi_az": True,
            "publicly_accessible": False
        }
        
        rds_actual = {
            "identifier": "app-db",
            "instance_class": "db.t3.medium",
            "engine": "postgres",
            "engine_version": "13.4",
            "storage_encrypted": True,
            "backup_retention_period": 3,  # Reduced
            "multi_az": False,  # Disabled
            "publicly_accessible": False
        }
        
        rds = platform.tracker.track(
            "aws_db_instance", "app-db", "aws",
            rds_expected, rds_actual
        )
        print(f"  ✓ {rds.resource_type}/{rds.name}")
        
        # Detect drift
        print("\n🔍 Detecting Drift...")
        
        report = await platform.detect_drift()
        
        print(f"\n  Drift Report: {report.report_id}")
        print(f"  Resources Checked: {report.resources_checked}")
        print(f"  Resources Drifted: {report.resources_drifted}")
        print(f"  Duration: {report.duration_seconds:.3f}s")
        
        # Show changes by severity
        print("\n  Changes by Severity:")
        print(f"    🔴 Critical: {report.critical_count}")
        print(f"    🟠 High: {report.high_count}")
        print(f"    🟡 Medium: {report.medium_count}")
        print(f"    🟢 Low: {report.low_count}")
        
        # Show changes by type
        print("\n  Changes by Type:")
        print(f"    ➕ Added: {report.added_count}")
        print(f"    ➖ Removed: {report.removed_count}")
        print(f"    📝 Modified: {report.modified_count}")
        
        # Show detailed changes
        print("\n📋 Drift Details:")
        print("  ┌──────────────────────────────────────────────────────────────────────┐")
        print("  │ Resource               │ Attribute           │ Type     │ Severity  │")
        print("  ├──────────────────────────────────────────────────────────────────────┤")
        
        for change in report.changes:
            resource = platform.tracker.resources.get(change.resource_id)
            res_name = f"{resource.resource_type}/{resource.name}"[:22].ljust(22) if resource else "-".ljust(22)
            attr = change.attribute_path[:19].ljust(19)
            dtype = change.drift_type.value[:8].ljust(8)
            sev = change.severity.value[:9].ljust(9)
            print(f"  │ {res_name} │ {attr} │ {dtype} │ {sev} │")
            
        print("  └──────────────────────────────────────────────────────────────────────┘")
        
        # Show value changes
        print("\n📊 Value Changes:")
        
        for change in report.changes[:5]:
            resource = platform.tracker.resources.get(change.resource_id)
            res_name = f"{resource.resource_type}/{resource.name}" if resource else "Unknown"
            
            severity_icon = {
                DriftSeverity.CRITICAL: "🔴",
                DriftSeverity.HIGH: "🟠",
                DriftSeverity.MEDIUM: "🟡",
                DriftSeverity.LOW: "🟢"
            }
            
            icon = severity_icon.get(change.severity, "⚪")
            print(f"\n  {icon} {res_name}")
            print(f"     Attribute: {change.attribute_path}")
            print(f"     Expected: {change.expected_value}")
            print(f"     Actual: {change.actual_value}")
            
        # Generate remediations
        print("\n🔧 Remediation Suggestions:")
        
        for change in report.changes[:3]:
            resource = platform.tracker.resources.get(change.resource_id)
            if resource:
                remediation = platform.remediation.suggest(resource, change)
                
                risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                icon = risk_icon.get(remediation.risk_level, "⚪")
                
                print(f"\n  {icon} {remediation.action.value}")
                print(f"     {remediation.description[:60]}...")
                if remediation.commands:
                    print(f"     Commands:")
                    for cmd in remediation.commands:
                        print(f"       $ {cmd}")
                        
        # Show alerts
        print("\n🚨 Active Alerts:")
        
        active_alerts = platform.alerts.get_active_alerts()
        print(f"\n  Total active: {len(active_alerts)}")
        
        for alert in active_alerts[:5]:
            severity_icon = {
                DriftSeverity.CRITICAL: "🔴",
                DriftSeverity.HIGH: "🟠",
                DriftSeverity.MEDIUM: "🟡",
                DriftSeverity.LOW: "🟢"
            }
            icon = severity_icon.get(alert.severity, "⚪")
            print(f"  {icon} [{alert.alert_id}] {alert.message[:50]}...")
            
        # Resource status
        print("\n📊 Resource Status:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │ Resource                    │ Status    │ Drifts │ Provider │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        
        for resource in platform.tracker.resources.values():
            name = f"{resource.resource_type}/{resource.name}"[:27].ljust(27)
            status = resource.status.value[:9].ljust(9)
            drifts = len(resource.drift_attributes)
            provider = resource.provider[:8].ljust(8)
            
            status_icon = "✓" if not resource.drifted else "✗"
            print(f"  │ {status_icon} {name} │ {status} │ {drifts:6} │ {provider} │")
            
        print("  └─────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📊 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        compliance_rate = (
            stats['compliant_resources'] / stats['total_resources'] * 100
        ) if stats['total_resources'] > 0 else 0
        
        print(f"\n  Total Resources: {stats['total_resources']}")
        print(f"  Drifted: {stats['drifted_resources']}")
        print(f"  Compliant: {stats['compliant_resources']}")
        print(f"  Compliance Rate: {compliance_rate:.1f}%")
        print(f"  Active Alerts: {stats['active_alerts']}")
        print(f"  Remediations: {stats['remediations']}")
        
        # Dashboard
        print("\n📋 Infrastructure Drift Dashboard:")
        print("  ┌────────────────────────────────────────────────────────────┐")
        print("  │              Infrastructure Drift Overview                 │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Total Resources:         {stats['total_resources']:>10}                   │")
        print(f"  │ Drifted Resources:       {stats['drifted_resources']:>10}                   │")
        print(f"  │ Compliance Rate:         {compliance_rate:>10.1f}%                  │")
        print("  ├────────────────────────────────────────────────────────────┤")
        print(f"  │ Active Alerts:           {stats['active_alerts']:>10}                   │")
        print(f"  │ Pending Remediations:    {stats['remediations']:>10}                   │")
        print(f"  │ Total Reports:           {stats['reports']:>10}                   │")
        print("  └────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Infrastructure Drift Detection Platform initialized!")
    print("=" * 60)
