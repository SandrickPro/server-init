#!/usr/bin/env python3
"""
Server Init - Iteration 193: Schema Registry Platform
Платформа реестра схем

Функционал:
- Schema Management - управление схемами
- Version Control - контроль версий
- Compatibility Check - проверка совместимости
- Schema Validation - валидация схем
- Evolution Policies - политики эволюции
- Schema References - ссылки на схемы
- Format Support - поддержка форматов (Avro, JSON, Protobuf)
- Schema Analytics - аналитика схем
"""

import asyncio
import random
import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class SchemaFormat(Enum):
    """Формат схемы"""
    AVRO = "avro"
    JSON = "json"
    PROTOBUF = "protobuf"
    THRIFT = "thrift"
    XML = "xml"


class CompatibilityMode(Enum):
    """Режим совместимости"""
    NONE = "none"
    BACKWARD = "backward"
    BACKWARD_TRANSITIVE = "backward_transitive"
    FORWARD = "forward"
    FORWARD_TRANSITIVE = "forward_transitive"
    FULL = "full"
    FULL_TRANSITIVE = "full_transitive"


class EvolutionType(Enum):
    """Тип эволюции"""
    ADD_FIELD = "add_field"
    REMOVE_FIELD = "remove_field"
    RENAME_FIELD = "rename_field"
    CHANGE_TYPE = "change_type"
    ADD_DEFAULT = "add_default"
    REMOVE_DEFAULT = "remove_default"


class ValidationResult(Enum):
    """Результат валидации"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class SchemaField:
    """Поле схемы"""
    name: str
    field_type: str
    nullable: bool = False
    default: Optional[Any] = None
    description: str = ""
    
    # Nested type
    nested_schema_id: Optional[str] = None
    
    # Array/Map
    items_type: Optional[str] = None
    
    # Constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None


@dataclass
class Schema:
    """Схема"""
    schema_id: str
    
    # Identity
    subject: str = ""
    version: int = 1
    
    # Content
    schema_format: SchemaFormat = SchemaFormat.JSON
    schema_text: str = ""
    schema_hash: str = ""
    
    # Fields
    fields: List[SchemaField] = field(default_factory=list)
    
    # Metadata
    namespace: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # References
    references: List[str] = field(default_factory=list)  # schema_ids
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # Status
    is_deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    
    def compute_hash(self):
        """Вычисление хеша"""
        content = f"{self.schema_format.value}|{self.schema_text}"
        self.schema_hash = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class SchemaVersion:
    """Версия схемы"""
    version_id: str
    schema_id: str
    version_number: int
    
    # Content
    schema_text: str = ""
    schema_hash: str = ""
    
    # Changes
    changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class CompatibilityReport:
    """Отчёт о совместимости"""
    report_id: str
    
    # Schemas
    source_schema_id: str = ""
    target_schema_id: str = ""
    
    # Result
    is_compatible: bool = True
    compatibility_mode: CompatibilityMode = CompatibilityMode.FULL
    
    # Issues
    issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # Breaking changes
    breaking_changes: List[str] = field(default_factory=list)
    
    # Timestamp
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subject:
    """Субъект (topic/entity)"""
    subject_id: str
    name: str = ""
    
    # Compatibility
    compatibility_mode: CompatibilityMode = CompatibilityMode.BACKWARD
    
    # Schemas
    schema_versions: List[str] = field(default_factory=list)  # schema_ids
    latest_version: int = 0
    
    # Metadata
    description: str = ""
    owner: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


class SchemaStore:
    """Хранилище схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Schema] = {}
        self.subjects: Dict[str, Subject] = {}
        self.versions: Dict[str, SchemaVersion] = {}
        
    def register(self, subject_name: str, schema_text: str,
                schema_format: SchemaFormat = SchemaFormat.JSON,
                created_by: str = "") -> Schema:
        """Регистрация схемы"""
        # Get or create subject
        subject = self._get_or_create_subject(subject_name)
        
        # Check if schema already exists
        schema_hash = hashlib.sha256(
            f"{schema_format.value}|{schema_text}".encode()
        ).hexdigest()[:16]
        
        for schema_id in subject.schema_versions:
            if schema_id in self.schemas:
                existing = self.schemas[schema_id]
                if existing.schema_hash == schema_hash:
                    return existing  # Return existing schema
                    
        # Create new schema
        subject.latest_version += 1
        
        schema = Schema(
            schema_id=f"schema_{uuid.uuid4().hex[:8]}",
            subject=subject_name,
            version=subject.latest_version,
            schema_format=schema_format,
            schema_text=schema_text,
            created_by=created_by
        )
        schema.compute_hash()
        
        # Parse fields (simplified)
        schema.fields = self._parse_fields(schema_text, schema_format)
        
        self.schemas[schema.schema_id] = schema
        subject.schema_versions.append(schema.schema_id)
        
        # Create version record
        version = SchemaVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            schema_id=schema.schema_id,
            version_number=schema.version,
            schema_text=schema_text,
            schema_hash=schema.schema_hash,
            created_by=created_by
        )
        self.versions[version.version_id] = version
        
        return schema
        
    def _get_or_create_subject(self, name: str) -> Subject:
        """Получение или создание субъекта"""
        if name not in self.subjects:
            subject = Subject(
                subject_id=f"subj_{uuid.uuid4().hex[:8]}",
                name=name
            )
            self.subjects[name] = subject
        return self.subjects[name]
        
    def _parse_fields(self, schema_text: str, 
                     schema_format: SchemaFormat) -> List[SchemaField]:
        """Парсинг полей (упрощённый)"""
        fields = []
        
        try:
            if schema_format == SchemaFormat.JSON:
                parsed = json.loads(schema_text)
                if "properties" in parsed:
                    for name, props in parsed["properties"].items():
                        fields.append(SchemaField(
                            name=name,
                            field_type=props.get("type", "string"),
                            nullable="null" in props.get("type", []),
                            description=props.get("description", "")
                        ))
        except:
            pass
            
        return fields
        
    def get_schema(self, schema_id: str) -> Optional[Schema]:
        """Получение схемы по ID"""
        return self.schemas.get(schema_id)
        
    def get_latest(self, subject_name: str) -> Optional[Schema]:
        """Получение последней версии"""
        subject = self.subjects.get(subject_name)
        if not subject or not subject.schema_versions:
            return None
        return self.schemas.get(subject.schema_versions[-1])
        
    def get_by_version(self, subject_name: str, version: int) -> Optional[Schema]:
        """Получение по версии"""
        subject = self.subjects.get(subject_name)
        if not subject:
            return None
            
        for schema_id in subject.schema_versions:
            schema = self.schemas.get(schema_id)
            if schema and schema.version == version:
                return schema
        return None


class CompatibilityChecker:
    """Проверка совместимости"""
    
    def __init__(self, store: SchemaStore):
        self.store = store
        
    def check(self, new_schema: Schema, 
             mode: CompatibilityMode = CompatibilityMode.BACKWARD) -> CompatibilityReport:
        """Проверка совместимости"""
        report = CompatibilityReport(
            report_id=f"compat_{uuid.uuid4().hex[:8]}",
            source_schema_id=new_schema.schema_id,
            compatibility_mode=mode
        )
        
        # Get previous schema
        subject = self.store.subjects.get(new_schema.subject)
        if not subject or len(subject.schema_versions) < 2:
            report.is_compatible = True
            return report
            
        previous_schema_id = subject.schema_versions[-2]
        previous_schema = self.store.schemas.get(previous_schema_id)
        
        if not previous_schema:
            report.is_compatible = True
            return report
            
        report.target_schema_id = previous_schema_id
        
        # Check based on mode
        if mode == CompatibilityMode.BACKWARD:
            self._check_backward(new_schema, previous_schema, report)
        elif mode == CompatibilityMode.FORWARD:
            self._check_forward(new_schema, previous_schema, report)
        elif mode == CompatibilityMode.FULL:
            self._check_backward(new_schema, previous_schema, report)
            self._check_forward(new_schema, previous_schema, report)
            
        report.is_compatible = len(report.breaking_changes) == 0
        return report
        
    def _check_backward(self, new_schema: Schema, old_schema: Schema, 
                       report: CompatibilityReport):
        """Проверка обратной совместимости"""
        old_fields = {f.name: f for f in old_schema.fields}
        new_fields = {f.name: f for f in new_schema.fields}
        
        # Check removed fields
        for name, old_field in old_fields.items():
            if name not in new_fields:
                report.breaking_changes.append(
                    f"Field '{name}' was removed"
                )
                
        # Check type changes
        for name, new_field in new_fields.items():
            if name in old_fields:
                old_field = old_fields[name]
                if old_field.field_type != new_field.field_type:
                    report.breaking_changes.append(
                        f"Field '{name}' type changed from {old_field.field_type} to {new_field.field_type}"
                    )
                    
        # Check new required fields
        for name, new_field in new_fields.items():
            if name not in old_fields and not new_field.nullable and new_field.default is None:
                report.issues.append({
                    "type": "warning",
                    "message": f"New required field '{name}' without default"
                })
                
    def _check_forward(self, new_schema: Schema, old_schema: Schema,
                      report: CompatibilityReport):
        """Проверка прямой совместимости"""
        old_fields = {f.name: f for f in old_schema.fields}
        new_fields = {f.name: f for f in new_schema.fields}
        
        # Check added required fields
        for name, new_field in new_fields.items():
            if name not in old_fields and not new_field.nullable:
                report.issues.append({
                    "type": "forward_issue",
                    "message": f"New field '{name}' not readable by old schema"
                })


class SchemaValidator:
    """Валидатор схем"""
    
    def validate_schema(self, schema: Schema) -> Dict[str, Any]:
        """Валидация схемы"""
        issues = []
        warnings = []
        
        # Check schema text
        if not schema.schema_text:
            issues.append("Schema text is empty")
            
        # Check fields
        if not schema.fields:
            warnings.append("Schema has no fields defined")
            
        # Check for duplicate fields
        field_names = [f.name for f in schema.fields]
        duplicates = set([n for n in field_names if field_names.count(n) > 1])
        if duplicates:
            issues.append(f"Duplicate field names: {duplicates}")
            
        # Validate JSON schema
        if schema.schema_format == SchemaFormat.JSON:
            try:
                json.loads(schema.schema_text)
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON: {str(e)}")
                
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
        
    def validate_data(self, schema: Schema, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных по схеме"""
        issues = []
        
        # Check required fields
        for field in schema.fields:
            if not field.nullable and field.default is None:
                if field.name not in data:
                    issues.append(f"Missing required field: {field.name}")
                    
        # Check types (simplified)
        for field in schema.fields:
            if field.name in data:
                value = data[field.name]
                expected_type = field.field_type
                
                if expected_type == "string" and not isinstance(value, str):
                    issues.append(f"Field {field.name} should be string")
                elif expected_type == "integer" and not isinstance(value, int):
                    issues.append(f"Field {field.name} should be integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    issues.append(f"Field {field.name} should be boolean")
                    
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


class SchemaEvolutionAnalyzer:
    """Анализатор эволюции схем"""
    
    def __init__(self, store: SchemaStore):
        self.store = store
        
    def analyze_evolution(self, subject_name: str) -> List[Dict[str, Any]]:
        """Анализ эволюции"""
        subject = self.store.subjects.get(subject_name)
        if not subject or len(subject.schema_versions) < 2:
            return []
            
        evolution = []
        
        for i in range(1, len(subject.schema_versions)):
            prev_id = subject.schema_versions[i - 1]
            curr_id = subject.schema_versions[i]
            
            prev_schema = self.store.schemas.get(prev_id)
            curr_schema = self.store.schemas.get(curr_id)
            
            if not prev_schema or not curr_schema:
                continue
                
            changes = self._compare_schemas(prev_schema, curr_schema)
            
            evolution.append({
                "from_version": prev_schema.version,
                "to_version": curr_schema.version,
                "changes": changes,
                "timestamp": curr_schema.created_at
            })
            
        return evolution
        
    def _compare_schemas(self, old: Schema, new: Schema) -> List[Dict[str, Any]]:
        """Сравнение схем"""
        changes = []
        
        old_fields = {f.name: f for f in old.fields}
        new_fields = {f.name: f for f in new.fields}
        
        # Added fields
        for name in new_fields:
            if name not in old_fields:
                changes.append({
                    "type": EvolutionType.ADD_FIELD.value,
                    "field": name,
                    "details": f"Added field '{name}'"
                })
                
        # Removed fields
        for name in old_fields:
            if name not in new_fields:
                changes.append({
                    "type": EvolutionType.REMOVE_FIELD.value,
                    "field": name,
                    "details": f"Removed field '{name}'"
                })
                
        # Changed fields
        for name in old_fields:
            if name in new_fields:
                old_field = old_fields[name]
                new_field = new_fields[name]
                
                if old_field.field_type != new_field.field_type:
                    changes.append({
                        "type": EvolutionType.CHANGE_TYPE.value,
                        "field": name,
                        "details": f"Type changed from {old_field.field_type} to {new_field.field_type}"
                    })
                    
        return changes


class SchemaRegistryPlatform:
    """Платформа реестра схем"""
    
    def __init__(self):
        self.store = SchemaStore()
        self.compatibility = CompatibilityChecker(self.store)
        self.validator = SchemaValidator()
        self.evolution = SchemaEvolutionAnalyzer(self.store)
        
    def register_schema(self, subject: str, schema_text: str,
                       format: SchemaFormat = SchemaFormat.JSON) -> Tuple[Schema, CompatibilityReport]:
        """Регистрация схемы с проверкой"""
        # Register
        schema = self.store.register(subject, schema_text, format)
        
        # Check compatibility
        subject_obj = self.store.subjects.get(subject)
        mode = subject_obj.compatibility_mode if subject_obj else CompatibilityMode.BACKWARD
        
        report = self.compatibility.check(schema, mode)
        
        return schema, report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        schemas = list(self.store.schemas.values())
        
        by_format = {}
        by_subject = {}
        
        for schema in schemas:
            fmt = schema.schema_format.value
            by_format[fmt] = by_format.get(fmt, 0) + 1
            by_subject[schema.subject] = by_subject.get(schema.subject, 0) + 1
            
        return {
            "total_schemas": len(schemas),
            "total_subjects": len(self.store.subjects),
            "by_format": by_format,
            "by_subject": by_subject,
            "deprecated": len([s for s in schemas if s.is_deprecated])
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 193: Schema Registry Platform")
    print("=" * 60)
    
    platform = SchemaRegistryPlatform()
    print("✓ Schema Registry Platform created")
    
    # Register schemas
    print("\n📋 Registering Schemas...")
    
    # User schema v1
    user_schema_v1 = """{
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }"""
    
    schema1, report1 = platform.register_schema("user-events", user_schema_v1)
    print(f"  ✓ user-events v{schema1.version} registered")
    print(f"    Hash: {schema1.schema_hash}")
    print(f"    Fields: {len(schema1.fields)}")
    
    # User schema v2 (add field)
    user_schema_v2 = """{
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }"""
    
    schema2, report2 = platform.register_schema("user-events", user_schema_v2)
    print(f"  ✓ user-events v{schema2.version} registered")
    print(f"    Compatible: {report2.is_compatible}")
    
    # Order schema
    order_schema = """{
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "user_id": {"type": "string"},
            "total": {"type": "number"},
            "items": {"type": "array"},
            "status": {"type": "string"}
        },
        "required": ["order_id", "user_id", "total"]
    }"""
    
    schema3, _ = platform.register_schema("order-events", order_schema)
    print(f"  ✓ order-events v{schema3.version} registered")
    
    # Payment schema
    payment_schema = """{
        "type": "object",
        "properties": {
            "payment_id": {"type": "string"},
            "order_id": {"type": "string"},
            "amount": {"type": "number"},
            "method": {"type": "string"},
            "status": {"type": "string"}
        },
        "required": ["payment_id", "order_id", "amount"]
    }"""
    
    schema4, _ = platform.register_schema("payment-events", payment_schema)
    print(f"  ✓ payment-events v{schema4.version} registered")
    
    # Additional schemas
    schemas_data = [
        ("inventory-events", '{"type": "object", "properties": {"sku": {"type": "string"}, "quantity": {"type": "integer"}}}'),
        ("shipping-events", '{"type": "object", "properties": {"tracking_id": {"type": "string"}, "status": {"type": "string"}}}'),
        ("notification-events", '{"type": "object", "properties": {"user_id": {"type": "string"}, "message": {"type": "string"}}}'),
    ]
    
    for subject, schema_text in schemas_data:
        s, _ = platform.register_schema(subject, schema_text)
        print(f"  ✓ {subject} v{s.version} registered")
        
    # Schema details
    print("\n📊 Schema Details:")
    
    print("\n  ┌─────────────────────┬─────────┬────────┬─────────────────┬───────────┐")
    print("  │ Subject             │ Version │ Fields │ Hash            │ Format    │")
    print("  ├─────────────────────┼─────────┼────────┼─────────────────┼───────────┤")
    
    for schema in platform.store.schemas.values():
        subject = schema.subject[:19].ljust(19)
        version = str(schema.version).center(7)
        fields = str(len(schema.fields)).center(6)
        hash_val = schema.schema_hash[:15].ljust(15)
        fmt = schema.schema_format.value[:9].ljust(9)
        print(f"  │ {subject} │ {version} │ {fields} │ {hash_val} │ {fmt} │")
        
    print("  └─────────────────────┴─────────┴────────┴─────────────────┴───────────┘")
    
    # Compatibility check
    print("\n🔍 Compatibility Checking:")
    
    # Breaking change example
    breaking_schema = """{
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }"""
    
    schema_break, report_break = platform.register_schema("user-events", breaking_schema)
    
    print(f"\n  user-events v{schema_break.version}:")
    print(f"    Compatible: {report_break.is_compatible}")
    
    if report_break.breaking_changes:
        print("    Breaking Changes:")
        for change in report_break.breaking_changes:
            print(f"      ❌ {change}")
            
    if report_break.issues:
        print("    Issues:")
        for issue in report_break.issues:
            print(f"      ⚠️ {issue['message']}")
            
    # Schema validation
    print("\n✅ Schema Validation:")
    
    for schema in list(platform.store.schemas.values())[:5]:
        result = platform.validator.validate_schema(schema)
        status = "✓" if result["valid"] else "✗"
        print(f"  {status} {schema.subject} v{schema.version}")
        
        for issue in result["issues"]:
            print(f"      ❌ {issue}")
        for warning in result["warnings"]:
            print(f"      ⚠️ {warning}")
            
    # Data validation
    print("\n📝 Data Validation:")
    
    latest_user = platform.store.get_latest("user-events")
    
    test_data = [
        {"id": "user-1", "name": "John", "email": "john@example.com"},
        {"id": "user-2", "name": "Jane"},  # Missing email
        {"id": 123, "name": "Bob", "email": "bob@example.com"},  # Wrong type
    ]
    
    for data in test_data:
        result = platform.validator.validate_data(latest_user, data)
        status = "✓" if result["valid"] else "✗"
        print(f"  {status} {data}")
        for issue in result["issues"]:
            print(f"      ❌ {issue}")
            
    # Schema evolution
    print("\n📈 Schema Evolution Analysis:")
    
    evolution = platform.evolution.analyze_evolution("user-events")
    
    print(f"\n  Subject: user-events")
    print(f"  Total versions: {len(platform.store.subjects['user-events'].schema_versions)}")
    
    for ev in evolution:
        print(f"\n  v{ev['from_version']} → v{ev['to_version']}:")
        for change in ev["changes"]:
            print(f"    • {change['type']}: {change['details']}")
            
    # Subjects overview
    print("\n📋 Subjects Overview:")
    
    for name, subject in platform.store.subjects.items():
        print(f"\n  {name}:")
        print(f"    Versions: {subject.latest_version}")
        print(f"    Compatibility: {subject.compatibility_mode.value}")
        
        latest = platform.store.get_latest(name)
        if latest:
            print(f"    Latest Hash: {latest.schema_hash}")
            print(f"    Fields: {[f.name for f in latest.fields]}")
            
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Schemas: {stats['total_schemas']}")
    print(f"  Total Subjects: {stats['total_subjects']}")
    print(f"  Deprecated: {stats['deprecated']}")
    
    print("\n  By Format:")
    for fmt, count in stats['by_format'].items():
        bar = "█" * count + "░" * (10 - count)
        print(f"    {fmt:10} [{bar}] {count}")
        
    print("\n  By Subject:")
    for subject, count in sorted(stats['by_subject'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {subject}: {count} versions")
        
    # Field type distribution
    print("\n📊 Field Type Distribution:")
    
    field_types = {}
    for schema in platform.store.schemas.values():
        for f in schema.fields:
            ft = f.field_type
            field_types[ft] = field_types.get(ft, 0) + 1
            
    for ftype, count in sorted(field_types.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count, 15)
        print(f"    {ftype:10} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Schema Registry Dashboard                      │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Schemas:                 {stats['total_schemas']:>12}                        │")
    print(f"│ Total Subjects:                {stats['total_subjects']:>12}                        │")
    print(f"│ Deprecated Schemas:            {stats['deprecated']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    json_count = stats['by_format'].get('json', 0)
    print(f"│ JSON Schemas:                  {json_count:>12}                        │")
    print(f"│ Total Versions:                {len(platform.store.versions):>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Schema Registry Platform initialized!")
    print("=" * 60)
