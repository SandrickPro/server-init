#!/usr/bin/env python3
"""
Server Init - Iteration 250: gRPC Gateway Platform
Платформа gRPC шлюза с REST трансляцией

Функционал:
- Service Registration - регистрация сервисов
- Method Routing - маршрутизация методов
- HTTP/gRPC Translation - трансляция протоколов
- Streaming Support - поддержка стримов
- Load Balancing - балансировка нагрузки
- Health Checking - проверка здоровья
- Interceptors - перехватчики
- Metadata Handling - обработка метаданных
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid


class ServiceState(Enum):
    """Состояние сервиса"""
    UNKNOWN = "unknown"
    SERVING = "serving"
    NOT_SERVING = "not_serving"
    TRANSIENT_FAILURE = "transient_failure"


class MethodType(Enum):
    """Тип метода gRPC"""
    UNARY = "unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDIRECTIONAL = "bidirectional"


class CallStatus(Enum):
    """Статус вызова"""
    OK = "ok"
    CANCELLED = "cancelled"
    INVALID_ARGUMENT = "invalid_argument"
    DEADLINE_EXCEEDED = "deadline_exceeded"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    PERMISSION_DENIED = "permission_denied"
    UNAUTHENTICATED = "unauthenticated"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    UNAVAILABLE = "unavailable"
    INTERNAL = "internal"


class LoadBalancePolicy(Enum):
    """Политика балансировки"""
    ROUND_ROBIN = "round_robin"
    PICK_FIRST = "pick_first"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"


class HTTPMethod(Enum):
    """HTTP метод"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ProtobufMessage:
    """Protobuf сообщение"""
    message_id: str
    name: str
    package: str = ""
    
    # Fields
    fields: Dict[str, str] = field(default_factory=dict)  # name -> type
    
    # Nested
    nested_messages: List[str] = field(default_factory=list)
    enums: List[str] = field(default_factory=list)
    
    # Options
    deprecated: bool = False


@dataclass
class GRPCMethod:
    """gRPC метод"""
    method_id: str
    name: str
    full_name: str = ""
    
    # Type
    method_type: MethodType = MethodType.UNARY
    
    # Messages
    input_type: str = ""
    output_type: str = ""
    
    # HTTP mapping
    http_method: Optional[HTTPMethod] = None
    http_path: str = ""
    
    # Options
    deprecated: bool = False
    timeout_ms: int = 30000
    
    # Stats
    call_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0


@dataclass
class GRPCService:
    """gRPC сервис"""
    service_id: str
    name: str
    package: str = ""
    full_name: str = ""
    
    # Methods
    methods: Dict[str, GRPCMethod] = field(default_factory=dict)
    
    # State
    state: ServiceState = ServiceState.UNKNOWN
    
    # Endpoints
    endpoints: List[str] = field(default_factory=list)  # host:port
    
    # Options
    version: str = "1.0.0"
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    registered_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None


@dataclass
class ServiceEndpoint:
    """Endpoint сервиса"""
    endpoint_id: str
    address: str
    port: int
    
    # Service
    service_id: str = ""
    
    # State
    state: ServiceState = ServiceState.UNKNOWN
    
    # Load balancing
    weight: int = 100
    connections: int = 0
    
    # Stats
    requests_handled: int = 0
    errors: int = 0
    
    # Time
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class GRPCCall:
    """gRPC вызов"""
    call_id: str
    
    # Method
    service: str = ""
    method: str = ""
    method_type: MethodType = MethodType.UNARY
    
    # Messages
    request: Any = None
    response: Any = None
    
    # Status
    status: CallStatus = CallStatus.OK
    error_message: str = ""
    
    # Metadata
    request_metadata: Dict[str, str] = field(default_factory=dict)
    response_metadata: Dict[str, str] = field(default_factory=dict)
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    latency_ms: float = 0
    
    # Streaming
    messages_sent: int = 0
    messages_received: int = 0


@dataclass
class Interceptor:
    """Interceptor для gRPC"""
    interceptor_id: str
    name: str
    
    # Type
    client_side: bool = True
    server_side: bool = True
    
    # Order
    order: int = 0
    
    # Handler
    handler: Optional[Callable] = None
    
    # Stats
    calls_intercepted: int = 0
    
    # Options
    enabled: bool = True


@dataclass
class HTTPBinding:
    """HTTP привязка к gRPC методу"""
    binding_id: str
    
    # HTTP
    http_method: HTTPMethod = HTTPMethod.POST
    path_pattern: str = ""
    
    # gRPC
    service: str = ""
    method: str = ""
    
    # Body
    body_field: str = "*"  # * = entire request
    response_body: str = ""
    
    # Parameters
    path_params: List[str] = field(default_factory=list)
    query_params: List[str] = field(default_factory=list)
    
    # Stats
    request_count: int = 0


class GRPCGateway:
    """gRPC Gateway"""
    
    def __init__(self):
        self.services: Dict[str, GRPCService] = {}
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.methods: Dict[str, GRPCMethod] = {}
        self.messages: Dict[str, ProtobufMessage] = {}
        self.interceptors: Dict[str, Interceptor] = {}
        self.http_bindings: Dict[str, HTTPBinding] = {}
        self.calls: List[GRPCCall] = []
        
        # Load balancing
        self._lb_state: Dict[str, int] = {}  # service -> current index
        
    def register_service(self, name: str, package: str = "",
                        version: str = "1.0.0") -> GRPCService:
        """Регистрация сервиса"""
        full_name = f"{package}.{name}" if package else name
        
        service = GRPCService(
            service_id=f"svc_{uuid.uuid4().hex[:8]}",
            name=name,
            package=package,
            full_name=full_name,
            version=version
        )
        
        self.services[service.service_id] = service
        return service
        
    def add_method(self, service_id: str, name: str, method_type: MethodType,
                  input_type: str, output_type: str,
                  timeout_ms: int = 30000) -> Optional[GRPCMethod]:
        """Добавление метода к сервису"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        full_name = f"/{service.full_name}/{name}"
        
        method = GRPCMethod(
            method_id=f"mth_{uuid.uuid4().hex[:8]}",
            name=name,
            full_name=full_name,
            method_type=method_type,
            input_type=input_type,
            output_type=output_type,
            timeout_ms=timeout_ms
        )
        
        service.methods[method.method_id] = method
        self.methods[full_name] = method
        
        return method
        
    def add_endpoint(self, service_id: str, address: str,
                    port: int, weight: int = 100) -> Optional[ServiceEndpoint]:
        """Добавление endpoint к сервису"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        endpoint = ServiceEndpoint(
            endpoint_id=f"ep_{uuid.uuid4().hex[:8]}",
            address=address,
            port=port,
            service_id=service_id,
            weight=weight
        )
        
        self.endpoints[endpoint.endpoint_id] = endpoint
        service.endpoints.append(f"{address}:{port}")
        
        return endpoint
        
    def register_message(self, name: str, package: str,
                        fields: Dict[str, str]) -> ProtobufMessage:
        """Регистрация Protobuf сообщения"""
        full_name = f"{package}.{name}" if package else name
        
        message = ProtobufMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            name=name,
            package=package,
            fields=fields
        )
        
        self.messages[full_name] = message
        return message
        
    def add_http_binding(self, service_id: str, method_id: str,
                        http_method: HTTPMethod, path: str,
                        body_field: str = "*") -> Optional[HTTPBinding]:
        """Добавление HTTP привязки к методу"""
        service = self.services.get(service_id)
        if not service:
            return None
            
        method = service.methods.get(method_id)
        if not method:
            return None
            
        binding = HTTPBinding(
            binding_id=f"bind_{uuid.uuid4().hex[:8]}",
            http_method=http_method,
            path_pattern=path,
            service=service.full_name,
            method=method.name,
            body_field=body_field
        )
        
        # Extract path params
        import re
        binding.path_params = re.findall(r'\{(\w+)\}', path)
        
        method.http_method = http_method
        method.http_path = path
        
        self.http_bindings[f"{http_method.value}:{path}"] = binding
        return binding
        
    def register_interceptor(self, name: str, order: int = 0,
                            client_side: bool = True,
                            server_side: bool = True) -> Interceptor:
        """Регистрация interceptor"""
        interceptor = Interceptor(
            interceptor_id=f"int_{uuid.uuid4().hex[:8]}",
            name=name,
            order=order,
            client_side=client_side,
            server_side=server_side
        )
        
        self.interceptors[interceptor.interceptor_id] = interceptor
        return interceptor
        
    async def invoke(self, method_path: str, request: Any,
                    metadata: Dict[str, str] = None) -> GRPCCall:
        """Вызов gRPC метода"""
        method = self.methods.get(method_path)
        
        call = GRPCCall(
            call_id=f"call_{uuid.uuid4().hex[:8]}",
            request=request,
            request_metadata=metadata or {}
        )
        
        if not method:
            call.status = CallStatus.NOT_FOUND
            call.error_message = f"Method {method_path} not found"
            return call
            
        # Parse service from path
        parts = method_path.strip('/').split('/')
        if len(parts) >= 2:
            call.service = parts[0]
            call.method = parts[1]
            
        call.method_type = method.method_type
        
        # Run interceptors
        for interceptor in sorted(self.interceptors.values(), key=lambda x: x.order):
            if interceptor.enabled and interceptor.client_side:
                interceptor.calls_intercepted += 1
                
        # Simulate call
        latency = random.uniform(10, 200)
        await asyncio.sleep(latency / 1000)
        
        # Random status
        if random.random() < 0.95:
            call.status = CallStatus.OK
            call.response = {"result": "success", "data": request}
        else:
            call.status = random.choice([
                CallStatus.INTERNAL,
                CallStatus.UNAVAILABLE,
                CallStatus.DEADLINE_EXCEEDED
            ])
            call.error_message = f"Simulated error: {call.status.value}"
            method.error_count += 1
            
        call.completed_at = datetime.now()
        call.latency_ms = latency
        
        method.call_count += 1
        method.total_latency_ms += latency
        
        self.calls.append(call)
        return call
        
    async def invoke_http(self, http_method: HTTPMethod, path: str,
                         body: Any = None, query: Dict[str, str] = None) -> GRPCCall:
        """Вызов через HTTP"""
        # Find binding
        binding_key = f"{http_method.value}:{path}"
        binding = None
        
        # Try exact match first
        if binding_key in self.http_bindings:
            binding = self.http_bindings[binding_key]
        else:
            # Try pattern match
            for key, b in self.http_bindings.items():
                pattern = key.split(':')[1]
                if self._match_path(pattern, path):
                    binding = b
                    break
                    
        if not binding:
            call = GRPCCall(
                call_id=f"call_{uuid.uuid4().hex[:8]}",
                status=CallStatus.NOT_FOUND,
                error_message=f"No HTTP binding for {http_method.value} {path}"
            )
            return call
            
        binding.request_count += 1
        
        # Build gRPC path
        grpc_path = f"/{binding.service}/{binding.method}"
        
        return await self.invoke(grpc_path, body or {})
        
    def _match_path(self, pattern: str, path: str) -> bool:
        """Сопоставление пути с паттерном"""
        import re
        regex = re.sub(r'\{(\w+)\}', r'[^/]+', pattern)
        return bool(re.match(f"^{regex}$", path))
        
    def select_endpoint(self, service_id: str,
                       policy: LoadBalancePolicy = LoadBalancePolicy.ROUND_ROBIN) -> Optional[ServiceEndpoint]:
        """Выбор endpoint для балансировки"""
        service = self.services.get(service_id)
        if not service or not service.endpoints:
            return None
            
        endpoints = [
            ep for ep in self.endpoints.values()
            if ep.service_id == service_id and ep.state == ServiceState.SERVING
        ]
        
        if not endpoints:
            return None
            
        if policy == LoadBalancePolicy.ROUND_ROBIN:
            idx = self._lb_state.get(service_id, 0)
            endpoint = endpoints[idx % len(endpoints)]
            self._lb_state[service_id] = idx + 1
            return endpoint
            
        elif policy == LoadBalancePolicy.PICK_FIRST:
            return endpoints[0]
            
        elif policy == LoadBalancePolicy.WEIGHTED:
            total = sum(ep.weight for ep in endpoints)
            r = random.randint(0, total - 1)
            cumulative = 0
            for ep in endpoints:
                cumulative += ep.weight
                if r < cumulative:
                    return ep
            return endpoints[-1]
            
        elif policy == LoadBalancePolicy.LEAST_CONNECTIONS:
            return min(endpoints, key=lambda ep: ep.connections)
            
        return endpoints[0]
        
    async def health_check(self, service_id: str) -> ServiceState:
        """Проверка здоровья сервиса"""
        service = self.services.get(service_id)
        if not service:
            return ServiceState.UNKNOWN
            
        # Check all endpoints
        healthy_count = 0
        total = len(service.endpoints)
        
        for ep in self.endpoints.values():
            if ep.service_id == service_id:
                # Simulate health check
                if random.random() < 0.9:
                    ep.state = ServiceState.SERVING
                    healthy_count += 1
                else:
                    ep.state = ServiceState.NOT_SERVING
                    
        if healthy_count == total:
            service.state = ServiceState.SERVING
        elif healthy_count > 0:
            service.state = ServiceState.TRANSIENT_FAILURE
        else:
            service.state = ServiceState.NOT_SERVING
            
        service.last_health_check = datetime.now()
        return service.state
        
    def get_service_stats(self, service_id: str) -> Dict[str, Any]:
        """Статистика сервиса"""
        service = self.services.get(service_id)
        if not service:
            return {}
            
        total_calls = sum(m.call_count for m in service.methods.values())
        total_errors = sum(m.error_count for m in service.methods.values())
        total_latency = sum(m.total_latency_ms for m in service.methods.values())
        
        return {
            "service_id": service_id,
            "name": service.name,
            "state": service.state.value,
            "methods_count": len(service.methods),
            "endpoints_count": len(service.endpoints),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_calls * 100) if total_calls > 0 else 0,
            "avg_latency_ms": (total_latency / total_calls) if total_calls > 0 else 0
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_calls = len(self.calls)
        ok_calls = sum(1 for c in self.calls if c.status == CallStatus.OK)
        avg_latency = sum(c.latency_ms for c in self.calls) / total_calls if total_calls > 0 else 0
        
        serving = sum(1 for s in self.services.values() if s.state == ServiceState.SERVING)
        
        return {
            "services_total": len(self.services),
            "services_serving": serving,
            "methods_total": len(self.methods),
            "endpoints_total": len(self.endpoints),
            "interceptors_total": len(self.interceptors),
            "http_bindings": len(self.http_bindings),
            "total_calls": total_calls,
            "successful_calls": ok_calls,
            "success_rate": (ok_calls / total_calls * 100) if total_calls > 0 else 0,
            "avg_latency_ms": avg_latency
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 250: gRPC Gateway Platform")
    print("=" * 60)
    
    gateway = GRPCGateway()
    print("✓ gRPC Gateway created")
    
    # Register messages
    print("\n📝 Registering Protobuf Messages...")
    
    messages_data = [
        ("User", "users.v1", {"id": "string", "name": "string", "email": "string"}),
        ("CreateUserRequest", "users.v1", {"name": "string", "email": "string"}),
        ("GetUserRequest", "users.v1", {"id": "string"}),
        ("UserResponse", "users.v1", {"user": "User"}),
        ("ListUsersRequest", "users.v1", {"page": "int32", "limit": "int32"}),
        ("ListUsersResponse", "users.v1", {"users": "repeated User", "total": "int32"}),
    ]
    
    for name, pkg, fields in messages_data:
        gateway.register_message(name, pkg, fields)
        print(f"  📝 {pkg}.{name}")
        
    # Register services
    print("\n🔧 Registering Services...")
    
    services_data = [
        ("UserService", "users.v1", "1.2.0"),
        ("ProductService", "products.v1", "2.0.0"),
        ("OrderService", "orders.v1", "1.5.0"),
        ("NotificationService", "notifications.v1", "1.0.0"),
    ]
    
    services = []
    for name, pkg, version in services_data:
        svc = gateway.register_service(name, pkg, version)
        services.append(svc)
        print(f"  🔧 {name} v{version}")
        
    # Add methods
    print("\n📌 Adding Methods...")
    
    methods_config = [
        (services[0].service_id, "CreateUser", MethodType.UNARY, "CreateUserRequest", "UserResponse"),
        (services[0].service_id, "GetUser", MethodType.UNARY, "GetUserRequest", "UserResponse"),
        (services[0].service_id, "ListUsers", MethodType.UNARY, "ListUsersRequest", "ListUsersResponse"),
        (services[0].service_id, "StreamUsers", MethodType.SERVER_STREAMING, "ListUsersRequest", "UserResponse"),
        (services[1].service_id, "GetProduct", MethodType.UNARY, "GetProductRequest", "ProductResponse"),
        (services[1].service_id, "ListProducts", MethodType.UNARY, "ListProductsRequest", "ProductsResponse"),
        (services[2].service_id, "CreateOrder", MethodType.UNARY, "CreateOrderRequest", "OrderResponse"),
        (services[2].service_id, "StreamOrderStatus", MethodType.SERVER_STREAMING, "OrderStatusRequest", "OrderStatus"),
    ]
    
    methods = []
    for svc_id, name, mtype, inp, out in methods_config:
        method = gateway.add_method(svc_id, name, mtype, inp, out)
        if method:
            methods.append(method)
            svc = gateway.services.get(svc_id)
            print(f"  📌 {svc.name}/{name} ({mtype.value})")
            
    # Add endpoints
    print("\n🌐 Adding Endpoints...")
    
    for svc in services:
        for i in range(2):
            ep = gateway.add_endpoint(
                svc.service_id,
                f"10.0.{services.index(svc)}.{i + 1}",
                50051 + i
            )
            if ep:
                ep.state = ServiceState.SERVING
                print(f"  🌐 {svc.name} -> {ep.address}:{ep.port}")
                
    # Add HTTP bindings
    print("\n🔗 Adding HTTP Bindings...")
    
    user_svc = services[0]
    methods_dict = user_svc.methods
    method_list = list(methods_dict.values())
    
    if len(method_list) >= 3:
        binding1 = gateway.add_http_binding(
            user_svc.service_id,
            method_list[0].method_id,
            HTTPMethod.POST,
            "/v1/users"
        )
        print(f"  🔗 POST /v1/users -> CreateUser")
        
        binding2 = gateway.add_http_binding(
            user_svc.service_id,
            method_list[1].method_id,
            HTTPMethod.GET,
            "/v1/users/{id}"
        )
        print(f"  🔗 GET /v1/users/{{id}} -> GetUser")
        
        binding3 = gateway.add_http_binding(
            user_svc.service_id,
            method_list[2].method_id,
            HTTPMethod.GET,
            "/v1/users"
        )
        print(f"  🔗 GET /v1/users -> ListUsers")
        
    # Register interceptors
    print("\n🔌 Registering Interceptors...")
    
    interceptors_data = [
        ("auth_interceptor", 0, True, True),
        ("logging_interceptor", 1, True, True),
        ("metrics_interceptor", 2, True, True),
        ("retry_interceptor", 3, True, False),
    ]
    
    for name, order, client, server in interceptors_data:
        gateway.register_interceptor(name, order, client, server)
        print(f"  🔌 {name} (order: {order})")
        
    # Make gRPC calls
    print("\n📞 Making gRPC Calls...")
    
    call_paths = [
        "/users.v1.UserService/CreateUser",
        "/users.v1.UserService/GetUser",
        "/users.v1.UserService/ListUsers",
        "/products.v1.ProductService/GetProduct",
        "/orders.v1.OrderService/CreateOrder",
    ]
    
    for path in call_paths:
        call = await gateway.invoke(path, {"test": "data"})
        status = "✓" if call.status == CallStatus.OK else "✗"
        print(f"  {status} {path.split('/')[-1]}: {call.status.value} ({call.latency_ms:.1f}ms)")
        
    # Make HTTP calls
    print("\n🌐 Making HTTP Calls...")
    
    http_calls = [
        (HTTPMethod.POST, "/v1/users", {"name": "Test", "email": "test@example.com"}),
        (HTTPMethod.GET, "/v1/users/123", None),
        (HTTPMethod.GET, "/v1/users", None),
    ]
    
    for method, path, body in http_calls:
        call = await gateway.invoke_http(method, path, body)
        status = "✓" if call.status == CallStatus.OK else "✗"
        print(f"  {status} {method.value} {path}: {call.status.value}")
        
    # Health checks
    print("\n❤️ Health Checks...")
    
    for svc in services:
        state = await gateway.health_check(svc.service_id)
        icon = "🟢" if state == ServiceState.SERVING else "🔴"
        print(f"  {icon} {svc.name}: {state.value}")
        
    # Load balancing demo
    print("\n⚖️ Load Balancing...")
    
    for policy in LoadBalancePolicy:
        ep = gateway.select_endpoint(services[0].service_id, policy)
        if ep:
            print(f"  {policy.value}: {ep.address}:{ep.port}")
            
    # Display services
    print("\n📊 Services:")
    
    print("\n  ┌─────────────────────┬───────────┬──────────┬──────────┬──────────┐")
    print("  │ Service             │ Version   │ Methods  │ Endpts   │ State    │")
    print("  ├─────────────────────┼───────────┼──────────┼──────────┼──────────┤")
    
    for svc in gateway.services.values():
        name = svc.name[:19].ljust(19)
        version = svc.version[:9].ljust(9)
        methods_count = str(len(svc.methods))[:8].ljust(8)
        endpoints = str(len(svc.endpoints))[:8].ljust(8)
        state = svc.state.value[:8].ljust(8)
        
        print(f"  │ {name} │ {version} │ {methods_count} │ {endpoints} │ {state} │")
        
    print("  └─────────────────────┴───────────┴──────────┴──────────┴──────────┘")
    
    # Display methods
    print("\n📌 Methods:")
    
    print("\n  ┌──────────────────────────────┬─────────────────┬──────────┬──────────┐")
    print("  │ Method                       │ Type            │ Calls    │ Avg(ms)  │")
    print("  ├──────────────────────────────┼─────────────────┼──────────┼──────────┤")
    
    for method in list(gateway.methods.values())[:8]:
        name = method.full_name[-28:].ljust(28)
        mtype = method.method_type.value[:15].ljust(15)
        calls = str(method.call_count)[:8].ljust(8)
        avg_lat = f"{method.total_latency_ms / max(1, method.call_count):.1f}"[:8].ljust(8)
        
        print(f"  │ {name} │ {mtype} │ {calls} │ {avg_lat} │")
        
    print("  └──────────────────────────────┴─────────────────┴──────────┴──────────┘")
    
    # Display HTTP bindings
    print("\n🔗 HTTP Bindings:")
    
    for key, binding in gateway.http_bindings.items():
        print(f"  {binding.http_method.value:6s} {binding.path_pattern:25s} → {binding.service}/{binding.method}")
        
    # Service stats
    print("\n📊 Service Stats:")
    
    for svc in services[:2]:
        stats = gateway.get_service_stats(svc.service_id)
        print(f"\n  {svc.name}:")
        print(f"    Calls: {stats['total_calls']}, Errors: {stats['total_errors']}")
        print(f"    Error Rate: {stats['error_rate']:.1f}%, Avg Latency: {stats['avg_latency_ms']:.1f}ms")
        
    # Statistics
    print("\n📊 Gateway Statistics:")
    
    stats = gateway.get_statistics()
    
    print(f"\n  Services: {stats['services_total']} (serving: {stats['services_serving']})")
    print(f"  Methods: {stats['methods_total']}")
    print(f"  Endpoints: {stats['endpoints_total']}")
    print(f"  Interceptors: {stats['interceptors_total']}")
    print(f"  HTTP Bindings: {stats['http_bindings']}")
    
    print(f"\n  Total Calls: {stats['total_calls']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Avg Latency: {stats['avg_latency_ms']:.1f}ms")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                     gRPC Gateway Dashboard                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Services:                      {stats['services_total']:>12}                        │")
    print(f"│ Methods:                       {stats['methods_total']:>12}                        │")
    print(f"│ Endpoints:                     {stats['endpoints_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Calls:                   {stats['total_calls']:>12}                        │")
    print(f"│ Success Rate:                  {stats['success_rate']:>11.1f}%                        │")
    print(f"│ Avg Latency:                   {stats['avg_latency_ms']:>10.1f}ms                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("gRPC Gateway Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
