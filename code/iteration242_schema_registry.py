#!/usr/bin/env python3
"""
Server Init - Iteration 242: Schema Registry Platform
Платформа реестра схем данных

Функционал:
- Schema Registration - регистрация схем
- Version Management - управление версиями
- Compatibility Check - проверка совместимости
- Schema Evolution - эволюция схем
- Schema Validation - валидация схем
- Subject Management - управление субъектами
- Schema Types - поддержка разных типов схем
- Change History - история изменений
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid
import json
import hashlib


class SchemaType(Enum):
    """Тип схемы"""
    AVRO = "avro"
    JSON_SCHEMA = "json_schema"
    PROTOBUF = "protobuf"
    THRIFT = "thrift"


class CompatibilityMode(Enum):
    """Режим совместимости"""
    NONE = "none"
    BACKWARD = "backward"
    BACKWARD_TRANSITIVE = "backward_transitive"
    FORWARD = "forward"
    FORWARD_TRANSITIVE = "forward_transitive"
    FULL = "full"
    FULL_TRANSITIVE = "full_transitive"


class SchemaStatus(Enum):
    """Статус схемы"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class ValidationStatus(Enum):
    """Статус валидации"""
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class SchemaField:
    """Поле схемы"""
    name: str
    field_type: str = "string"
    is_required: bool = True
    default_value: Any = None
    description: str = ""
    order: int = 0


@dataclass
class Schema:
    """Схема"""
    schema_id: str
    schema_hash: str = ""
    
    # Type
    schema_type: SchemaType = SchemaType.JSON_SCHEMA
    
    # Content
    schema_definition: str = ""
    
    # Fields (parsed)
    fields: List[SchemaField] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    # References
    references: List[str] = field(default_factory=list)


@dataclass
class SchemaVersion:
    """Версия схемы"""
    version_id: str
    version_number: int = 1
    
    # Schema
    schema: Optional[Schema] = None
    
    # Subject
    subject: str = ""
    
    # Status
    status: SchemaStatus = SchemaStatus.ACTIVE
    
    # Time
    registered_at: datetime = field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    
    # Compatibility
    compatible_with: List[int] = field(default_factory=list)


@dataclass
class Subject:
    """Субъект (логическая группа схем)"""
    subject_id: str
    name: str = ""
    
    # Compatibility
    compatibility: CompatibilityMode = CompatibilityMode.BACKWARD
    
    # Versions
    versions: Dict[int, SchemaVersion] = field(default_factory=dict)
    latest_version: int = 0
    
    # Metadata
    description: str = ""
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CompatibilityResult:
    """Результат проверки совместимости"""
    is_compatible: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Details
    breaking_changes: List[str] = field(default_factory=list)
    new_fields: List[str] = field(default_factory=list)
    removed_fields: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Результат валидации"""
    status: ValidationStatus = ValidationStatus.VALID
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class SchemaChange:
    """Изменение схемы"""
    change_id: str
    subject: str = ""
    
    # Versions
    from_version: int = 0
    to_version: int = 0
    
    # Type
    change_type: str = ""  # added, modified, removed
    
    # Details
    field_changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Time
    changed_at: datetime = field(default_factory=datetime.now)
    changed_by: str = ""


class SchemaRegistryPlatform:
    """Платформа реестра схем"""
    
    def __init__(self):
        self.schemas: Dict[str, Schema] = {}
        self.subjects: Dict[str, Subject] = {}
        self.changes: List[SchemaChange] = []
        
        # Global config
        self.default_compatibility = CompatibilityMode.BACKWARD
        
    def _compute_hash(self, definition: str) -> str:
        """Вычисление хеша схемы"""
        normalized = definition.strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
        
    def _parse_schema_fields(self, definition: str, 
                            schema_type: SchemaType) -> List[SchemaField]:
        """Парсинг полей схемы"""
        fields = []
        
        # Simplified parsing for demo
        try:
            if schema_type == SchemaType.JSON_SCHEMA:
                data = json.loads(definition)
                properties = data.get("properties", {})
                required = data.get("required", [])
                
                for i, (name, props) in enumerate(properties.items()):
                    fields.append(SchemaField(
                        name=name,
                        field_type=props.get("type", "string"),
                        is_required=name in required,
                        default_value=props.get("default"),
                        description=props.get("description", ""),
                        order=i
                    ))
        except:
            pass
            
        return fields
        
    def create_subject(self, name: str, 
                      compatibility: CompatibilityMode = None,
                      description: str = "",
                      owner: str = "",
                      tags: List[str] = None) -> Subject:
        """Создание субъекта"""
        subject = Subject(
            subject_id=f"subj_{uuid.uuid4().hex[:8]}",
            name=name,
            compatibility=compatibility or self.default_compatibility,
            description=description,
            owner=owner,
            tags=tags or []
        )
        
        self.subjects[name] = subject
        return subject
        
    def register_schema(self, subject_name: str,
                       definition: str,
                       schema_type: SchemaType = SchemaType.JSON_SCHEMA,
                       created_by: str = "") -> Optional[SchemaVersion]:
        """Регистрация схемы"""
        # Get or create subject
        if subject_name not in self.subjects:
            self.create_subject(subject_name)
            
        subject = self.subjects[subject_name]
        
        # Compute hash
        schema_hash = self._compute_hash(definition)
        
        # Check if same schema already exists
        for version in subject.versions.values():
            if version.schema and version.schema.schema_hash == schema_hash:
                return version
                
        # Parse fields
        fields = self._parse_schema_fields(definition, schema_type)
        
        # Create schema
        schema = Schema(
            schema_id=f"sch_{uuid.uuid4().hex[:8]}",
            schema_hash=schema_hash,
            schema_type=schema_type,
            schema_definition=definition,
            fields=fields,
            created_by=created_by
        )
        
        self.schemas[schema.schema_id] = schema
        
        # Check compatibility
        if subject.latest_version > 0:
            latest = subject.versions.get(subject.latest_version)
            if latest and latest.schema:
                compat = self.check_compatibility(
                    latest.schema, schema, subject.compatibility
                )
                if not compat.is_compatible:
                    return None
                    
        # Create version
        version_number = subject.latest_version + 1
        
        version = SchemaVersion(
            version_id=f"ver_{uuid.uuid4().hex[:8]}",
            version_number=version_number,
            schema=schema,
            subject=subject_name,
            compatible_with=list(range(1, version_number))
        )
        
        subject.versions[version_number] = version
        subject.latest_version = version_number
        subject.updated_at = datetime.now()
        
        # Record change
        if version_number > 1:
            self._record_change(subject_name, version_number - 1, version_number)
            
        return version
        
    def check_compatibility(self, old_schema: Schema, new_schema: Schema,
                           mode: CompatibilityMode) -> CompatibilityResult:
        """Проверка совместимости схем"""
        result = CompatibilityResult()
        
        if mode == CompatibilityMode.NONE:
            return result
            
        old_fields = {f.name: f for f in old_schema.fields}
        new_fields = {f.name: f for f in new_schema.fields}
        
        # Check removed fields
        for name, field in old_fields.items():
            if name not in new_fields:
                result.removed_fields.append(name)
                if field.is_required:
                    if mode in [CompatibilityMode.BACKWARD, 
                               CompatibilityMode.BACKWARD_TRANSITIVE,
                               CompatibilityMode.FULL,
                               CompatibilityMode.FULL_TRANSITIVE]:
                        result.breaking_changes.append(
                            f"Required field '{name}' was removed"
                        )
                        result.is_compatible = False
                        
        # Check new fields
        for name, field in new_fields.items():
            if name not in old_fields:
                result.new_fields.append(name)
                if field.is_required and field.default_value is None:
                    if mode in [CompatibilityMode.FORWARD,
                               CompatibilityMode.FORWARD_TRANSITIVE,
                               CompatibilityMode.FULL,
                               CompatibilityMode.FULL_TRANSITIVE]:
                        result.breaking_changes.append(
                            f"New required field '{name}' without default"
                        )
                        result.is_compatible = False
                        
        # Check type changes
        for name in set(old_fields.keys()) & set(new_fields.keys()):
            if old_fields[name].field_type != new_fields[name].field_type:
                result.breaking_changes.append(
                    f"Field '{name}' type changed from "
                    f"'{old_fields[name].field_type}' to "
                    f"'{new_fields[name].field_type}'"
                )
                result.is_compatible = False
                
        if not result.is_compatible:
            result.errors = result.breaking_changes
            
        return result
        
    def validate_schema(self, definition: str,
                       schema_type: SchemaType) -> ValidationResult:
        """Валидация схемы"""
        result = ValidationResult()
        
        try:
            if schema_type == SchemaType.JSON_SCHEMA:
                data = json.loads(definition)
                
                # Check required fields
                if "type" not in data:
                    result.warnings.append("Missing 'type' field")
                    
                if data.get("type") == "object" and "properties" not in data:
                    result.warnings.append("Object type without properties")
                    
            result.status = ValidationStatus.WARNING if result.warnings else ValidationStatus.VALID
            
        except json.JSONDecodeError as e:
            result.status = ValidationStatus.INVALID
            result.errors.append(f"Invalid JSON: {str(e)}")
            
        except Exception as e:
            result.status = ValidationStatus.INVALID
            result.errors.append(str(e))
            
        return result
        
    def _record_change(self, subject: str, from_ver: int, to_ver: int):
        """Запись изменения"""
        subj = self.subjects.get(subject)
        if not subj:
            return
            
        old_ver = subj.versions.get(from_ver)
        new_ver = subj.versions.get(to_ver)
        
        if not old_ver or not new_ver or not old_ver.schema or not new_ver.schema:
            return
            
        old_fields = {f.name: f for f in old_ver.schema.fields}
        new_fields = {f.name: f for f in new_ver.schema.fields}
        
        field_changes = []
        
        # Added
        for name in set(new_fields.keys()) - set(old_fields.keys()):
            field_changes.append({
                "type": "added",
                "field": name,
                "new_type": new_fields[name].field_type
            })
            
        # Removed
        for name in set(old_fields.keys()) - set(new_fields.keys()):
            field_changes.append({
                "type": "removed",
                "field": name,
                "old_type": old_fields[name].field_type
            })
            
        # Modified
        for name in set(old_fields.keys()) & set(new_fields.keys()):
            if old_fields[name].field_type != new_fields[name].field_type:
                field_changes.append({
                    "type": "modified",
                    "field": name,
                    "old_type": old_fields[name].field_type,
                    "new_type": new_fields[name].field_type
                })
                
        change = SchemaChange(
            change_id=f"chg_{uuid.uuid4().hex[:8]}",
            subject=subject,
            from_version=from_ver,
            to_version=to_ver,
            change_type="evolution",
            field_changes=field_changes
        )
        
        self.changes.append(change)
        
    def get_schema(self, subject: str, version: int = None) -> Optional[Schema]:
        """Получение схемы"""
        subj = self.subjects.get(subject)
        if not subj:
            return None
            
        ver_num = version or subj.latest_version
        ver = subj.versions.get(ver_num)
        
        return ver.schema if ver else None
        
    def get_subject_versions(self, subject: str) -> List[SchemaVersion]:
        """Получение версий субъекта"""
        subj = self.subjects.get(subject)
        if not subj:
            return []
            
        return list(subj.versions.values())
        
    def deprecate_schema(self, subject: str, version: int) -> bool:
        """Пометка схемы как устаревшей"""
        subj = self.subjects.get(subject)
        if not subj:
            return False
            
        ver = subj.versions.get(version)
        if not ver:
            return False
            
        ver.status = SchemaStatus.DEPRECATED
        ver.deprecated_at = datetime.now()
        return True
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_versions = sum(len(s.versions) for s in self.subjects.values())
        
        # By type
        by_type = {}
        for schema in self.schemas.values():
            t = schema.schema_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
        # By compatibility
        by_compat = {}
        for subj in self.subjects.values():
            c = subj.compatibility.value
            by_compat[c] = by_compat.get(c, 0) + 1
            
        return {
            "total_subjects": len(self.subjects),
            "total_schemas": len(self.schemas),
            "total_versions": total_versions,
            "total_changes": len(self.changes),
            "by_type": by_type,
            "by_compatibility": by_compat
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 242: Schema Registry Platform")
    print("=" * 60)
    
    platform = SchemaRegistryPlatform()
    print("✓ Schema Registry Platform created")
    
    # Create subjects
    print("\n📁 Creating Subjects...")
    
    subjects_data = [
        ("user-events", CompatibilityMode.BACKWARD, "User event schemas", "team-platform"),
        ("order-events", CompatibilityMode.FULL, "Order processing schemas", "team-orders"),
        ("payment-events", CompatibilityMode.BACKWARD_TRANSITIVE, "Payment schemas", "team-payments"),
        ("inventory-events", CompatibilityMode.FORWARD, "Inventory schemas", "team-warehouse"),
    ]
    
    subjects = []
    for name, compat, desc, owner in subjects_data:
        subj = platform.create_subject(name, compat, desc, owner, ["events", "kafka"])
        subjects.append(subj)
        print(f"  📁 {name} ({compat.value})")
        
    # Register schemas
    print("\n📋 Registering Schemas...")
    
    # User events - v1
    user_schema_v1 = json.dumps({
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "name": {"type": "string", "description": "User name"},
            "email": {"type": "string", "description": "Email"}
        },
        "required": ["user_id", "name"]
    }, indent=2)
    
    v1 = platform.register_schema("user-events", user_schema_v1, 
                                  SchemaType.JSON_SCHEMA, "admin")
    print(f"  ✓ user-events v{v1.version_number}")
    
    # User events - v2 (add field)
    user_schema_v2 = json.dumps({
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "name": {"type": "string", "description": "User name"},
            "email": {"type": "string", "description": "Email"},
            "phone": {"type": "string", "description": "Phone number", "default": ""}
        },
        "required": ["user_id", "name"]
    }, indent=2)
    
    v2 = platform.register_schema("user-events", user_schema_v2,
                                  SchemaType.JSON_SCHEMA, "admin")
    print(f"  ✓ user-events v{v2.version_number}")
    
    # Order events
    order_schema = json.dumps({
        "type": "object",
        "properties": {
            "order_id": {"type": "string"},
            "user_id": {"type": "string"},
            "items": {"type": "array"},
            "total": {"type": "number"},
            "status": {"type": "string"}
        },
        "required": ["order_id", "user_id", "status"]
    }, indent=2)
    
    v = platform.register_schema("order-events", order_schema,
                                SchemaType.JSON_SCHEMA, "admin")
    print(f"  ✓ order-events v{v.version_number}")
    
    # Payment events
    payment_schema = json.dumps({
        "type": "object",
        "properties": {
            "payment_id": {"type": "string"},
            "order_id": {"type": "string"},
            "amount": {"type": "number"},
            "currency": {"type": "string"},
            "method": {"type": "string"}
        },
        "required": ["payment_id", "order_id", "amount"]
    }, indent=2)
    
    v = platform.register_schema("payment-events", payment_schema,
                                SchemaType.JSON_SCHEMA, "admin")
    print(f"  ✓ payment-events v{v.version_number}")
    
    # Inventory events
    inventory_schema = json.dumps({
        "type": "object",
        "properties": {
            "product_id": {"type": "string"},
            "warehouse_id": {"type": "string"},
            "quantity": {"type": "integer"},
            "operation": {"type": "string"}
        },
        "required": ["product_id", "quantity"]
    }, indent=2)
    
    v = platform.register_schema("inventory-events", inventory_schema,
                                SchemaType.JSON_SCHEMA, "admin")
    print(f"  ✓ inventory-events v{v.version_number}")
    
    # Validate schema
    print("\n🔍 Validating Schemas...")
    
    valid_result = platform.validate_schema(user_schema_v2, SchemaType.JSON_SCHEMA)
    print(f"  ✓ user-events v2: {valid_result.status.value}")
    
    invalid_schema = "{ invalid json"
    invalid_result = platform.validate_schema(invalid_schema, SchemaType.JSON_SCHEMA)
    print(f"  ❌ invalid schema: {invalid_result.status.value}")
    
    # Check compatibility
    print("\n🔄 Checking Compatibility...")
    
    old_schema = platform.get_schema("user-events", 1)
    new_schema = platform.get_schema("user-events", 2)
    
    compat = platform.check_compatibility(old_schema, new_schema, CompatibilityMode.BACKWARD)
    
    print(f"  Compatible: {compat.is_compatible}")
    print(f"  New fields: {compat.new_fields}")
    print(f"  Removed fields: {compat.removed_fields}")
    print(f"  Breaking changes: {len(compat.breaking_changes)}")
    
    # Display subjects
    print("\n📊 Registered Subjects:")
    
    print("\n  ┌───────────────────┬──────────────────────┬─────────┬──────────┬─────────────┐")
    print("  │ Subject           │ Compatibility        │ Versions│ Owner    │ Status      │")
    print("  ├───────────────────┼──────────────────────┼─────────┼──────────┼─────────────┤")
    
    for name, subj in platform.subjects.items():
        subject = name[:17].ljust(17)
        compat = subj.compatibility.value[:20].ljust(20)
        versions = str(subj.latest_version).ljust(7)
        owner = subj.owner[:8].ljust(8)
        status = "🟢 Active"
        
        print(f"  │ {subject} │ {compat} │ {versions} │ {owner} │ {status:11s} │")
        
    print("  └───────────────────┴──────────────────────┴─────────┴──────────┴─────────────┘")
    
    # Display versions
    print("\n📋 Schema Versions:")
    
    for name, subj in platform.subjects.items():
        print(f"\n  📁 {name}")
        
        for ver_num, version in subj.versions.items():
            status_icon = "🟢" if version.status == SchemaStatus.ACTIVE else "🟡"
            schema = version.schema
            
            print(f"    {status_icon} v{ver_num}: {len(schema.fields)} fields, hash={schema.schema_hash[:8]}")
            
            for field in schema.fields[:3]:
                required = "*" if field.is_required else ""
                print(f"       • {field.name}{required}: {field.field_type}")
                
    # Display changes
    print("\n📜 Schema Changes:")
    
    for change in platform.changes[:5]:
        print(f"\n  🔄 {change.subject}: v{change.from_version} → v{change.to_version}")
        
        for fc in change.field_changes:
            if fc['type'] == 'added':
                print(f"     ➕ Added: {fc['field']} ({fc['new_type']})")
            elif fc['type'] == 'removed':
                print(f"     ➖ Removed: {fc['field']}")
            elif fc['type'] == 'modified':
                print(f"     ✏️ Modified: {fc['field']}: {fc['old_type']} → {fc['new_type']}")
                
    # Schema evolution example
    print("\n🔄 Schema Evolution Example:")
    
    print("\n  user-events:")
    print("  ┌─────────────────────────────────────────────────────────────────┐")
    print("  │ v1                           │ v2                              │")
    print("  │ ─────────────────────────────│─────────────────────────────────│")
    print("  │ user_id: string (required)   │ user_id: string (required)      │")
    print("  │ name: string (required)      │ name: string (required)         │")
    print("  │ email: string                │ email: string                   │")
    print("  │                              │ phone: string (default: '')  ✨ │")
    print("  └─────────────────────────────────────────────────────────────────┘")
    print("  ✓ Backward compatible: old readers can read new data")
    
    # Compatibility matrix
    print("\n📊 Compatibility Matrix:")
    
    print("\n  ┌─────────────────────┬────────────┬─────────────┬──────────────┐")
    print("  │ Mode                │ Add Field  │ Remove Field│ Change Type  │")
    print("  ├─────────────────────┼────────────┼─────────────┼──────────────┤")
    print("  │ NONE                │ ✅         │ ✅          │ ✅           │")
    print("  │ BACKWARD            │ ✅*        │ ❌          │ ❌           │")
    print("  │ FORWARD             │ ❌         │ ✅*         │ ❌           │")
    print("  │ FULL                │ ✅**       │ ✅**        │ ❌           │")
    print("  └─────────────────────┴────────────┴─────────────┴──────────────┘")
    print("  * with default value, ** with optional field")
    
    # Statistics
    print("\n📊 Platform Statistics:")
    
    stats = platform.get_statistics()
    
    print(f"\n  Total Subjects: {stats['total_subjects']}")
    print(f"  Total Schemas: {stats['total_schemas']}")
    print(f"  Total Versions: {stats['total_versions']}")
    print(f"  Total Changes: {stats['total_changes']}")
    
    # By type
    print("\n  Schemas by Type:")
    for schema_type, count in stats['by_type'].items():
        bar = "█" * count + "░" * (10 - count)
        print(f"    {schema_type:15s} [{bar}] {count}")
        
    # By compatibility
    print("\n  Subjects by Compatibility:")
    for compat, count in stats['by_compatibility'].items():
        bar = "█" * count + "░" * (10 - count)
        print(f"    {compat:20s} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     Schema Registry Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Subjects:                {stats['total_subjects']:>12}                        │")
    print(f"│ Total Schemas:                 {stats['total_schemas']:>12}                        │")
    print(f"│ Total Versions:                {stats['total_versions']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Schema Changes:                {stats['total_changes']:>12}                        │")
    print(f"│ Default Compatibility:            backward                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Schema Registry Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
