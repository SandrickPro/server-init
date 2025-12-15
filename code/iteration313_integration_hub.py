#!/usr/bin/env python3
"""
Server Init - Iteration 313: Integration Hub Platform
Платформа интеграций

Функционал:
- Connectors - коннекторы к системам
- Data Mapping - маппинг данных
- Transformations - трансформации
- Event Bus - шина событий
- API Gateway - API шлюз
- Webhooks - вебхуки
- Message Queues - очереди сообщений
- Monitoring - мониторинг интеграций
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class ConnectorType(Enum):
    """Тип коннектора"""
    REST_API = "rest_api"
    SOAP = "soap"
    GRAPHQL = "graphql"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE = "file"
    SFTP = "sftp"
    EMAIL = "email"
    WEBHOOK = "webhook"


class ConnectorStatus(Enum):
    """Статус коннектора"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"


class EventType(Enum):
    """Тип события"""
    DATA_SYNC = "data_sync"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    ERROR = "error"


class TransformationType(Enum):
    """Тип трансформации"""
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    SPLIT = "split"
    MERGE = "merge"
    ENRICH = "enrich"


class FlowStatus(Enum):
    """Статус потока"""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DRAFT = "draft"


@dataclass
class Connector:
    """Коннектор"""
    connector_id: str
    name: str
    connector_type: ConnectorType
    
    # Connection
    connection_config: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"url": "...", "auth": {...}}
    
    # Status
    status: ConnectorStatus = ConnectorStatus.DISCONNECTED
    last_connected: Optional[datetime] = None
    error_message: str = ""
    
    # Stats
    requests_count: int = 0
    errors_count: int = 0
    last_request: Optional[datetime] = None
    avg_response_time_ms: float = 0
    
    # Health
    health_check_interval: int = 60
    last_health_check: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataMapping:
    """Маппинг данных"""
    mapping_id: str
    name: str
    
    # Source/Target
    source_schema: Dict[str, Any] = field(default_factory=dict)
    target_schema: Dict[str, Any] = field(default_factory=dict)
    
    # Field mappings
    field_mappings: List[Dict[str, Any]] = field(default_factory=list)
    # e.g., [{"source": "firstName", "target": "first_name", "transform": "lowercase"}]
    
    # Default values
    defaults: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transformation:
    """Трансформация"""
    transform_id: str
    name: str
    transform_type: TransformationType
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"field": "price", "operation": "multiply", "value": 1.1}
    
    # Order
    order: int = 0


@dataclass
class IntegrationFlow:
    """Поток интеграции"""
    flow_id: str
    name: str
    description: str
    
    # Source/Target
    source_connector_id: str = ""
    target_connector_id: str = ""
    
    # Processing
    mapping_id: str = ""
    transformations: List[str] = field(default_factory=list)  # transform_ids
    
    # Trigger
    trigger_type: EventType = EventType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    # Schedule: {"cron": "*/5 * * * *"}
    # Webhook: {"path": "/webhook/..."}
    
    # Status
    status: FlowStatus = FlowStatus.DRAFT
    
    # Error handling
    retry_count: int = 3
    error_handler: str = ""  # flow_id for error handling
    
    # Stats
    executions_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_execution: Optional[datetime] = None
    avg_execution_time_ms: float = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FlowExecution:
    """Выполнение потока"""
    execution_id: str
    flow_id: str
    
    # Status
    status: str = "running"  # running, completed, failed
    
    # Data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Records
    records_processed: int = 0
    records_success: int = 0
    records_failed: int = 0
    
    # Error
    error_message: str = ""
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    duration_ms: float = 0


@dataclass
class Event:
    """Событие"""
    event_id: str
    event_type: EventType
    source: str = ""
    
    # Data
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Routing
    target_flows: List[str] = field(default_factory=list)
    
    # Status
    processed: bool = False
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Webhook:
    """Вебхук"""
    webhook_id: str
    name: str
    
    # Config
    path: str = ""
    method: str = "POST"
    secret: str = ""
    
    # Target
    target_flow_id: str = ""
    
    # Status
    is_active: bool = True
    
    # Stats
    calls_count: int = 0
    last_call: Optional[datetime] = None


class IntegrationHub:
    """Хаб интеграций"""
    
    def __init__(self):
        self.connectors: Dict[str, Connector] = {}
        self.mappings: Dict[str, DataMapping] = {}
        self.transformations: Dict[str, Transformation] = {}
        self.flows: Dict[str, IntegrationFlow] = {}
        self.executions: Dict[str, FlowExecution] = {}
        self.events: Dict[str, Event] = {}
        self.webhooks: Dict[str, Webhook] = {}
        
    async def create_connector(self, name: str,
                              connector_type: ConnectorType,
                              connection_config: Dict[str, Any] = None) -> Connector:
        """Создание коннектора"""
        connector = Connector(
            connector_id=f"conn_{uuid.uuid4().hex[:8]}",
            name=name,
            connector_type=connector_type,
            connection_config=connection_config or {}
        )
        
        self.connectors[connector.connector_id] = connector
        return connector
        
    async def connect(self, connector_id: str) -> bool:
        """Подключение коннектора"""
        connector = self.connectors.get(connector_id)
        if not connector:
            return False
            
        connector.status = ConnectorStatus.CONNECTING
        
        # Simulate connection
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        if random.random() > 0.1:  # 90% success
            connector.status = ConnectorStatus.CONNECTED
            connector.last_connected = datetime.now()
            return True
        else:
            connector.status = ConnectorStatus.ERROR
            connector.error_message = "Connection failed"
            return False
            
    async def create_mapping(self, name: str,
                            source_schema: Dict[str, Any],
                            target_schema: Dict[str, Any],
                            field_mappings: List[Dict[str, Any]] = None) -> DataMapping:
        """Создание маппинга"""
        mapping = DataMapping(
            mapping_id=f"map_{uuid.uuid4().hex[:8]}",
            name=name,
            source_schema=source_schema,
            target_schema=target_schema,
            field_mappings=field_mappings or []
        )
        
        self.mappings[mapping.mapping_id] = mapping
        return mapping
        
    async def create_transformation(self, name: str,
                                   transform_type: TransformationType,
                                   config: Dict[str, Any] = None,
                                   order: int = 0) -> Transformation:
        """Создание трансформации"""
        transform = Transformation(
            transform_id=f"tr_{uuid.uuid4().hex[:8]}",
            name=name,
            transform_type=transform_type,
            config=config or {},
            order=order
        )
        
        self.transformations[transform.transform_id] = transform
        return transform
        
    async def create_flow(self, name: str,
                         description: str = "",
                         source_connector_id: str = "",
                         target_connector_id: str = "",
                         mapping_id: str = "",
                         trigger_type: EventType = EventType.MANUAL) -> IntegrationFlow:
        """Создание потока интеграции"""
        flow = IntegrationFlow(
            flow_id=f"flow_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            source_connector_id=source_connector_id,
            target_connector_id=target_connector_id,
            mapping_id=mapping_id,
            trigger_type=trigger_type
        )
        
        self.flows[flow.flow_id] = flow
        return flow
        
    async def add_transformation_to_flow(self, flow_id: str,
                                        transform_id: str) -> bool:
        """Добавление трансформации в поток"""
        flow = self.flows.get(flow_id)
        transform = self.transformations.get(transform_id)
        
        if not flow or not transform:
            return False
            
        if transform_id not in flow.transformations:
            flow.transformations.append(transform_id)
            
        return True
        
    async def activate_flow(self, flow_id: str) -> bool:
        """Активация потока"""
        flow = self.flows.get(flow_id)
        if not flow:
            return False
            
        flow.status = FlowStatus.ACTIVE
        return True
        
    async def execute_flow(self, flow_id: str,
                          input_data: Dict[str, Any] = None) -> Optional[FlowExecution]:
        """Выполнение потока"""
        flow = self.flows.get(flow_id)
        if not flow or flow.status != FlowStatus.ACTIVE:
            return None
            
        execution = FlowExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:8]}",
            flow_id=flow_id,
            input_data=input_data or {}
        )
        
        self.executions[execution.execution_id] = execution
        
        try:
            # Process data
            data = dict(input_data or {})
            records = data.get("records", [data])
            
            execution.records_processed = len(records)
            
            # Apply mapping
            if flow.mapping_id:
                mapping = self.mappings.get(flow.mapping_id)
                if mapping:
                    data = await self._apply_mapping(data, mapping)
                    
            # Apply transformations
            for transform_id in flow.transformations:
                transform = self.transformations.get(transform_id)
                if transform:
                    data = await self._apply_transformation(data, transform)
                    
            # Simulate processing time
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            execution.output_data = data
            execution.records_success = execution.records_processed
            execution.status = "completed"
            
            flow.success_count += 1
            
            # Update connector stats
            source = self.connectors.get(flow.source_connector_id)
            if source:
                source.requests_count += 1
                source.last_request = datetime.now()
                
            target = self.connectors.get(flow.target_connector_id)
            if target:
                target.requests_count += 1
                target.last_request = datetime.now()
                
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            flow.failure_count += 1
            
        execution.completed_at = datetime.now()
        execution.duration_ms = (
            execution.completed_at - execution.started_at
        ).total_seconds() * 1000
        
        flow.executions_count += 1
        flow.last_execution = datetime.now()
        
        # Update average execution time
        total_time = flow.avg_execution_time_ms * (flow.executions_count - 1) + execution.duration_ms
        flow.avg_execution_time_ms = total_time / flow.executions_count
        
        return execution
        
    async def _apply_mapping(self, data: Dict[str, Any],
                            mapping: DataMapping) -> Dict[str, Any]:
        """Применение маппинга"""
        result = dict(mapping.defaults)
        
        for field_map in mapping.field_mappings:
            source_field = field_map.get("source", "")
            target_field = field_map.get("target", source_field)
            transform = field_map.get("transform", "")
            
            if source_field in data:
                value = data[source_field]
                
                if transform == "lowercase":
                    value = str(value).lower()
                elif transform == "uppercase":
                    value = str(value).upper()
                elif transform == "trim":
                    value = str(value).strip()
                    
                result[target_field] = value
                
        return result
        
    async def _apply_transformation(self, data: Dict[str, Any],
                                   transform: Transformation) -> Dict[str, Any]:
        """Применение трансформации"""
        config = transform.config
        
        if transform.transform_type == TransformationType.MAP:
            field = config.get("field", "")
            operation = config.get("operation", "")
            value = config.get("value", 0)
            
            if field in data:
                if operation == "multiply":
                    data[field] = data[field] * value
                elif operation == "add":
                    data[field] = data[field] + value
                    
        elif transform.transform_type == TransformationType.FILTER:
            # Filter implementation
            pass
            
        elif transform.transform_type == TransformationType.ENRICH:
            enrichment = config.get("enrichment", {})
            data.update(enrichment)
            
        return data
        
    async def create_webhook(self, name: str,
                            path: str,
                            target_flow_id: str,
                            method: str = "POST") -> Optional[Webhook]:
        """Создание вебхука"""
        flow = self.flows.get(target_flow_id)
        if not flow:
            return None
            
        webhook = Webhook(
            webhook_id=f"wh_{uuid.uuid4().hex[:8]}",
            name=name,
            path=path,
            target_flow_id=target_flow_id,
            method=method,
            secret=uuid.uuid4().hex
        )
        
        self.webhooks[webhook.webhook_id] = webhook
        return webhook
        
    async def trigger_webhook(self, webhook_id: str,
                             payload: Dict[str, Any]) -> Optional[FlowExecution]:
        """Активация вебхука"""
        webhook = self.webhooks.get(webhook_id)
        if not webhook or not webhook.is_active:
            return None
            
        webhook.calls_count += 1
        webhook.last_call = datetime.now()
        
        # Create event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=EventType.WEBHOOK,
            source=f"webhook:{webhook.name}",
            payload=payload,
            target_flows=[webhook.target_flow_id]
        )
        
        self.events[event.event_id] = event
        
        # Execute flow
        execution = await self.execute_flow(webhook.target_flow_id, payload)
        
        event.processed = True
        
        return execution
        
    async def publish_event(self, event_type: EventType,
                           source: str,
                           payload: Dict[str, Any],
                           target_flows: List[str] = None) -> Event:
        """Публикация события"""
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            source=source,
            payload=payload,
            target_flows=target_flows or []
        )
        
        self.events[event.event_id] = event
        
        # Execute target flows
        for flow_id in event.target_flows:
            await self.execute_flow(flow_id, payload)
            
        event.processed = True
        
        return event
        
    def get_flow_status(self, flow_id: str) -> Dict[str, Any]:
        """Статус потока"""
        flow = self.flows.get(flow_id)
        if not flow:
            return {}
            
        source = self.connectors.get(flow.source_connector_id)
        target = self.connectors.get(flow.target_connector_id)
        
        success_rate = 0
        if flow.executions_count > 0:
            success_rate = flow.success_count / flow.executions_count * 100
            
        return {
            "flow_id": flow_id,
            "name": flow.name,
            "status": flow.status.value,
            "source": source.name if source else "N/A",
            "target": target.name if target else "N/A",
            "trigger": flow.trigger_type.value,
            "executions": flow.executions_count,
            "success_rate": success_rate,
            "avg_time_ms": flow.avg_execution_time_ms,
            "last_execution": flow.last_execution.isoformat() if flow.last_execution else None
        }
        
    def get_connector_health(self, connector_id: str) -> Dict[str, Any]:
        """Здоровье коннектора"""
        connector = self.connectors.get(connector_id)
        if not connector:
            return {}
            
        error_rate = 0
        if connector.requests_count > 0:
            error_rate = connector.errors_count / connector.requests_count * 100
            
        return {
            "connector_id": connector_id,
            "name": connector.name,
            "type": connector.connector_type.value,
            "status": connector.status.value,
            "requests": connector.requests_count,
            "errors": connector.errors_count,
            "error_rate": error_rate,
            "avg_response_ms": connector.avg_response_time_ms,
            "last_connected": connector.last_connected.isoformat() if connector.last_connected else None
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_connector_type = {}
        for c in self.connectors.values():
            by_connector_type[c.connector_type.value] = by_connector_type.get(c.connector_type.value, 0) + 1
            
        by_flow_status = {}
        total_executions = 0
        total_success = 0
        
        for f in self.flows.values():
            by_flow_status[f.status.value] = by_flow_status.get(f.status.value, 0) + 1
            total_executions += f.executions_count
            total_success += f.success_count
            
        by_event_type = {}
        for e in self.events.values():
            by_event_type[e.event_type.value] = by_event_type.get(e.event_type.value, 0) + 1
            
        connected = sum(1 for c in self.connectors.values() if c.status == ConnectorStatus.CONNECTED)
        
        return {
            "total_connectors": len(self.connectors),
            "connectors_connected": connected,
            "by_connector_type": by_connector_type,
            "total_mappings": len(self.mappings),
            "total_transformations": len(self.transformations),
            "total_flows": len(self.flows),
            "by_flow_status": by_flow_status,
            "total_executions": total_executions,
            "total_success": total_success,
            "success_rate": (total_success / total_executions * 100) if total_executions > 0 else 0,
            "total_webhooks": len(self.webhooks),
            "total_events": len(self.events),
            "by_event_type": by_event_type
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 313: Integration Hub Platform")
    print("=" * 60)
    
    hub = IntegrationHub()
    print("✓ Integration Hub created")
    
    # Create connectors
    print("\n🔌 Creating Connectors...")
    
    connectors_data = [
        ("Salesforce API", ConnectorType.REST_API, {"url": "https://salesforce.com/api", "auth": "oauth2"}),
        ("SAP HANA", ConnectorType.DATABASE, {"host": "sap-hana.local", "port": 30015}),
        ("Stripe API", ConnectorType.REST_API, {"url": "https://api.stripe.com", "auth": "api_key"}),
        ("Kafka", ConnectorType.MESSAGE_QUEUE, {"brokers": ["kafka1:9092", "kafka2:9092"]}),
        ("AWS S3", ConnectorType.FILE, {"bucket": "data-lake", "region": "us-east-1"}),
        ("PostgreSQL", ConnectorType.DATABASE, {"host": "pg.local", "port": 5432}),
        ("HubSpot", ConnectorType.REST_API, {"url": "https://api.hubspot.com"}),
        ("Slack", ConnectorType.WEBHOOK, {"webhook_url": "https://hooks.slack.com/..."}),
    ]
    
    connectors = []
    for name, c_type, config in connectors_data:
        connector = await hub.create_connector(name, c_type, config)
        connectors.append(connector)
        print(f"  🔌 {name} ({c_type.value})")
        
    # Connect connectors
    print("\n🔗 Connecting...")
    
    for connector in connectors:
        await hub.connect(connector.connector_id)
        
    connected = sum(1 for c in connectors if c.status == ConnectorStatus.CONNECTED)
    print(f"  ✓ Connected: {connected}/{len(connectors)}")
    
    # Create mappings
    print("\n🗺️ Creating Mappings...")
    
    mappings_data = [
        ("Salesforce to PostgreSQL", 
         {"id": "string", "Name": "string", "Email": "string"},
         {"customer_id": "string", "name": "string", "email": "string"},
         [{"source": "id", "target": "customer_id"},
          {"source": "Name", "target": "name", "transform": "trim"},
          {"source": "Email", "target": "email", "transform": "lowercase"}]),
        ("Stripe to SAP",
         {"amount": "number", "currency": "string", "customer": "string"},
         {"payment_amount": "number", "currency_code": "string", "customer_ref": "string"},
         [{"source": "amount", "target": "payment_amount"},
          {"source": "currency", "target": "currency_code", "transform": "uppercase"},
          {"source": "customer", "target": "customer_ref"}])
    ]
    
    mappings = []
    for name, source, target, fields in mappings_data:
        mapping = await hub.create_mapping(name, source, target, fields)
        mappings.append(mapping)
        print(f"  🗺️ {name}")
        
    # Create transformations
    print("\n🔄 Creating Transformations...")
    
    transforms_data = [
        ("Price Markup", TransformationType.MAP, {"field": "price", "operation": "multiply", "value": 1.2}),
        ("Add Timestamp", TransformationType.ENRICH, {"enrichment": {"processed_at": "{{now}}"}}),
        ("Filter Active", TransformationType.FILTER, {"field": "status", "value": "active"})
    ]
    
    transforms = []
    for name, t_type, config in transforms_data:
        transform = await hub.create_transformation(name, t_type, config)
        transforms.append(transform)
        print(f"  🔄 {name} ({t_type.value})")
        
    # Create flows
    print("\n📊 Creating Integration Flows...")
    
    flows_data = [
        ("CRM to Database Sync", "Sync customer data from Salesforce to PostgreSQL",
         connectors[0].connector_id, connectors[5].connector_id, mappings[0].mapping_id, EventType.SCHEDULED),
        ("Payment Processing", "Process Stripe payments to SAP",
         connectors[2].connector_id, connectors[1].connector_id, mappings[1].mapping_id, EventType.WEBHOOK),
        ("Event Bus Processor", "Process events from Kafka",
         connectors[3].connector_id, connectors[5].connector_id, None, EventType.DATA_SYNC),
        ("Data Lake Export", "Export data to S3",
         connectors[5].connector_id, connectors[4].connector_id, None, EventType.SCHEDULED),
        ("HubSpot Integration", "Sync HubSpot contacts",
         connectors[6].connector_id, connectors[5].connector_id, None, EventType.DATA_SYNC)
    ]
    
    flows = []
    for name, desc, source, target, mapping, trigger in flows_data:
        flow = await hub.create_flow(name, desc, source, target, mapping, trigger)
        flows.append(flow)
        
        # Add transformations
        for transform in transforms[:2]:
            await hub.add_transformation_to_flow(flow.flow_id, transform.transform_id)
            
        await hub.activate_flow(flow.flow_id)
        print(f"  📊 {name} ({trigger.value})")
        
    # Create webhooks
    print("\n🪝 Creating Webhooks...")
    
    webhooks_data = [
        ("Stripe Webhook", "/webhook/stripe", flows[1].flow_id),
        ("HubSpot Webhook", "/webhook/hubspot", flows[4].flow_id),
        ("Generic Webhook", "/webhook/generic", flows[2].flow_id)
    ]
    
    webhooks = []
    for name, path, flow_id in webhooks_data:
        webhook = await hub.create_webhook(name, path, flow_id)
        webhooks.append(webhook)
        print(f"  🪝 {name}: {path}")
        
    # Execute flows
    print("\n▶️ Executing Flows...")
    
    for _ in range(15):
        flow = random.choice(flows)
        
        test_data = {
            "id": f"rec_{random.randint(1000, 9999)}",
            "Name": f"Customer {random.randint(1, 100)}",
            "Email": f"user{random.randint(1, 100)}@example.com",
            "amount": random.randint(100, 10000),
            "currency": random.choice(["usd", "eur", "gbp"]),
            "customer": f"cus_{random.randint(1000, 9999)}",
            "price": random.uniform(10, 1000),
            "status": random.choice(["active", "inactive"])
        }
        
        await hub.execute_flow(flow.flow_id, test_data)
        
    completed = sum(1 for e in hub.executions.values() if e.status == "completed")
    failed = sum(1 for e in hub.executions.values() if e.status == "failed")
    print(f"  ✓ Completed: {completed} | Failed: {failed}")
    
    # Trigger webhooks
    print("\n🪝 Triggering Webhooks...")
    
    for webhook in webhooks:
        for _ in range(random.randint(2, 5)):
            await hub.trigger_webhook(webhook.webhook_id, {"event": "test", "data": {"id": random.randint(1, 100)}})
            
    print(f"  ✓ Triggered webhooks")
    
    # Publish events
    print("\n📤 Publishing Events...")
    
    events_data = [
        (EventType.DATA_SYNC, "database", {"table": "customers", "action": "update"}),
        (EventType.SCHEDULED, "scheduler", {"job": "daily_sync"}),
        (EventType.MANUAL, "user", {"action": "manual_trigger"})
    ]
    
    for e_type, source, payload in events_data:
        await hub.publish_event(e_type, source, payload, [flows[2].flow_id])
        print(f"  📤 {e_type.value} from {source}")
        
    # Connector health
    print("\n💚 Connector Health:")
    
    print("\n  ┌──────────────────────┬────────────┬────────────┬──────────┬────────────┐")
    print("  │ Connector            │ Type       │ Status     │ Requests │ Error Rate │")
    print("  ├──────────────────────┼────────────┼────────────┼──────────┼────────────┤")
    
    for connector in connectors:
        health = hub.get_connector_health(connector.connector_id)
        
        name = health['name'][:20].ljust(20)
        c_type = health['type'][:10].ljust(10)
        status = health['status'][:10].ljust(10)
        requests = str(health['requests']).ljust(8)
        error_rate = f"{health['error_rate']:.1f}%".ljust(10)
        
        print(f"  │ {name} │ {c_type} │ {status} │ {requests} │ {error_rate} │")
        
    print("  └──────────────────────┴────────────┴────────────┴──────────┴────────────┘")
    
    # Flow status
    print("\n📊 Flow Status:")
    
    print("\n  ┌────────────────────────────┬──────────┬───────────┬─────────────┬────────────┐")
    print("  │ Flow                       │ Status   │ Executions│ Success     │ Avg Time   │")
    print("  ├────────────────────────────┼──────────┼───────────┼─────────────┼────────────┤")
    
    for flow in flows:
        status = hub.get_flow_status(flow.flow_id)
        
        name = status['name'][:26].ljust(26)
        f_status = status['status'][:8].ljust(8)
        execs = str(status['executions']).ljust(9)
        success = f"{status['success_rate']:.0f}%".ljust(11)
        avg_time = f"{status['avg_time_ms']:.1f}ms".ljust(10)
        
        print(f"  │ {name} │ {f_status} │ {execs} │ {success} │ {avg_time} │")
        
    print("  └────────────────────────────┴──────────┴───────────┴─────────────┴────────────┘")
    
    # Webhook stats
    print("\n🪝 Webhook Stats:")
    
    for webhook in webhooks:
        last_call = webhook.last_call.strftime('%H:%M:%S') if webhook.last_call else "Never"
        active = "✓" if webhook.is_active else "✗"
        
        print(f"  [{active}] {webhook.name}")
        print(f"      Path: {webhook.path} | Calls: {webhook.calls_count} | Last: {last_call}")
        
    # Event distribution
    print("\n📤 Event Distribution:")
    
    stats = hub.get_statistics()
    
    for event_type, count in stats['by_event_type'].items():
        bar = "█" * min(count, 10) + "░" * (10 - min(count, 10))
        print(f"  {event_type:15} [{bar}] {count}")
        
    # Connector types distribution
    print("\n🔌 Connector Types Distribution:")
    
    for c_type, count in stats['by_connector_type'].items():
        bar = "█" * count + "░" * (5 - min(count, 5))
        print(f"  {c_type:15} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Hub Statistics:")
    
    print(f"\n  Total Connectors: {stats['total_connectors']}")
    print(f"  Connected: {stats['connectors_connected']}")
    
    print(f"\n  Total Mappings: {stats['total_mappings']}")
    print(f"  Total Transformations: {stats['total_transformations']}")
    
    print(f"\n  Total Flows: {stats['total_flows']}")
    print("  By Status:")
    for status_name, count in stats['by_flow_status'].items():
        print(f"    {status_name}: {count}")
        
    print(f"\n  Total Executions: {stats['total_executions']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    print(f"\n  Total Webhooks: {stats['total_webhooks']}")
    print(f"  Total Events: {stats['total_events']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Integration Hub Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Connectors:            {stats['total_connectors']:>12}                          │")
    print(f"│ Total Integration Flows:     {stats['total_flows']:>12}                          │")
    print(f"│ Total Executions:            {stats['total_executions']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Success Rate:                {stats['success_rate']:>10.1f}%                         │")
    print(f"│ Total Webhooks:              {stats['total_webhooks']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Integration Hub Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
