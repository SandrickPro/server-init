#!/usr/bin/env python3
"""
Server Init - Iteration 42: API Gateway & Management Platform
API Gateway и платформа управления API

Функционал:
- API Gateway Core - ядро API Gateway
- Request/Response Transformation - трансформация запросов/ответов
- Authentication & Authorization - аутентификация и авторизация
- Rate Limiting & Throttling - ограничение скорости и троттлинг
- API Versioning - версионирование API
- API Analytics - аналитика API
- Developer Portal - портал разработчика
- API Lifecycle Management - управление жизненным циклом API
"""

import json
import asyncio
import hashlib
import time
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Pattern
from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import defaultdict
import uuid
import base64
import hmac


class AuthType(Enum):
    """Тип аутентификации"""
    NONE = "none"
    API_KEY = "api_key"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    MTLS = "mtls"


class HTTPMethod(Enum):
    """HTTP метод"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIStatus(Enum):
    """Статус API"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class RateLimitStrategy(Enum):
    """Стратегия rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class APIRoute:
    """Маршрут API"""
    route_id: str
    path: str
    methods: List[HTTPMethod]
    
    # Backend
    backend_url: str
    backend_timeout_ms: int = 30000
    
    # Трансформации
    request_transformations: List[Dict[str, Any]] = field(default_factory=list)
    response_transformations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Аутентификация
    auth_required: bool = True
    auth_type: AuthType = AuthType.API_KEY
    
    # Rate Limiting
    rate_limit: Optional[Dict[str, Any]] = None
    
    # Кэширование
    cache_enabled: bool = False
    cache_ttl_seconds: int = 300
    
    # Валидация
    request_validation: Optional[Dict[str, Any]] = None
    response_validation: Optional[Dict[str, Any]] = None
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class API:
    """API"""
    api_id: str
    name: str
    version: str
    base_path: str
    
    # Маршруты
    routes: List[APIRoute] = field(default_factory=list)
    
    # Статус
    status: APIStatus = APIStatus.DRAFT
    
    # Документация
    description: str = ""
    openapi_spec: Optional[Dict[str, Any]] = None
    
    # Владение
    owner: str = ""
    team: str = ""
    
    # Настройки по умолчанию
    default_auth: AuthType = AuthType.API_KEY
    default_rate_limit: Optional[Dict[str, Any]] = None
    
    # CORS
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


@dataclass
class APIKey:
    """API ключ"""
    key_id: str
    key_hash: str
    name: str
    
    # Владелец
    owner: str = ""
    application: str = ""
    
    # Разрешения
    apis: List[str] = field(default_factory=list)  # Разрешённые API
    scopes: List[str] = field(default_factory=list)
    
    # Лимиты
    rate_limit_override: Optional[Dict[str, Any]] = None
    quota_limit: Optional[int] = None  # Запросов в месяц
    
    # Состояние
    enabled: bool = True
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    
    # Статистика
    request_count: int = 0


@dataclass
class OAuthClient:
    """OAuth клиент"""
    client_id: str
    client_secret_hash: str
    name: str
    
    # Настройки
    grant_types: List[str] = field(default_factory=lambda: ["client_credentials"])
    redirect_uris: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    
    # Время жизни токенов
    access_token_ttl: int = 3600
    refresh_token_ttl: int = 86400
    
    # Состояние
    enabled: bool = True
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class APIRequest:
    """API запрос"""
    request_id: str
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[Any]
    
    # Контекст
    client_ip: str = ""
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    
    # Время
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class APIResponse:
    """API ответ"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    
    # Метаданные
    latency_ms: float = 0.0
    cached: bool = False
    backend_latency_ms: float = 0.0


@dataclass
class APIAnalytics:
    """Аналитика API"""
    api_id: str
    period_start: datetime
    period_end: datetime
    
    # Метрики
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Латентность
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # По статусам
    status_codes: Dict[int, int] = field(default_factory=dict)
    
    # По эндпоинтам
    endpoints: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # По клиентам
    top_clients: List[Dict[str, Any]] = field(default_factory=list)
    
    # Ошибки
    errors: List[Dict[str, Any]] = field(default_factory=list)


class RequestTransformer:
    """Трансформатор запросов"""
    
    def __init__(self):
        self.transformers: Dict[str, Callable] = {}
        self._register_default_transformers()
        
    def _register_default_transformers(self):
        """Регистрация стандартных трансформеров"""
        self.transformers["add_header"] = self._add_header
        self.transformers["remove_header"] = self._remove_header
        self.transformers["rewrite_path"] = self._rewrite_path
        self.transformers["add_query_param"] = self._add_query_param
        self.transformers["transform_body"] = self._transform_body
        
    def transform(self, request: APIRequest, 
                  transformations: List[Dict[str, Any]]) -> APIRequest:
        """Применение трансформаций"""
        for transform in transformations:
            transform_type = transform.get("type")
            transformer = self.transformers.get(transform_type)
            
            if transformer:
                request = transformer(request, transform)
                
        return request
        
    def _add_header(self, request: APIRequest, config: Dict[str, Any]) -> APIRequest:
        """Добавление заголовка"""
        name = config.get("name", "")
        value = config.get("value", "")
        request.headers[name] = value
        return request
        
    def _remove_header(self, request: APIRequest, config: Dict[str, Any]) -> APIRequest:
        """Удаление заголовка"""
        name = config.get("name", "")
        request.headers.pop(name, None)
        return request
        
    def _rewrite_path(self, request: APIRequest, config: Dict[str, Any]) -> APIRequest:
        """Перезапись пути"""
        pattern = config.get("pattern", "")
        replacement = config.get("replacement", "")
        request.path = re.sub(pattern, replacement, request.path)
        return request
        
    def _add_query_param(self, request: APIRequest, config: Dict[str, Any]) -> APIRequest:
        """Добавление query параметра"""
        name = config.get("name", "")
        value = config.get("value", "")
        request.query_params[name] = value
        return request
        
    def _transform_body(self, request: APIRequest, config: Dict[str, Any]) -> APIRequest:
        """Трансформация тела"""
        if not request.body:
            return request
            
        # Добавление полей
        if "add_fields" in config:
            if isinstance(request.body, dict):
                request.body.update(config["add_fields"])
                
        # Удаление полей
        if "remove_fields" in config:
            if isinstance(request.body, dict):
                for field_name in config["remove_fields"]:
                    request.body.pop(field_name, None)
                    
        return request


class ResponseTransformer:
    """Трансформатор ответов"""
    
    def __init__(self):
        self.transformers: Dict[str, Callable] = {}
        self._register_default_transformers()
        
    def _register_default_transformers(self):
        """Регистрация стандартных трансформеров"""
        self.transformers["add_header"] = self._add_header
        self.transformers["remove_header"] = self._remove_header
        self.transformers["transform_body"] = self._transform_body
        self.transformers["mask_fields"] = self._mask_fields
        
    def transform(self, response: APIResponse,
                  transformations: List[Dict[str, Any]]) -> APIResponse:
        """Применение трансформаций"""
        for transform in transformations:
            transform_type = transform.get("type")
            transformer = self.transformers.get(transform_type)
            
            if transformer:
                response = transformer(response, transform)
                
        return response
        
    def _add_header(self, response: APIResponse, config: Dict[str, Any]) -> APIResponse:
        """Добавление заголовка"""
        name = config.get("name", "")
        value = config.get("value", "")
        response.headers[name] = value
        return response
        
    def _remove_header(self, response: APIResponse, config: Dict[str, Any]) -> APIResponse:
        """Удаление заголовка"""
        name = config.get("name", "")
        response.headers.pop(name, None)
        return response
        
    def _transform_body(self, response: APIResponse, config: Dict[str, Any]) -> APIResponse:
        """Трансформация тела"""
        if not response.body:
            return response
            
        if "add_fields" in config and isinstance(response.body, dict):
            response.body.update(config["add_fields"])
            
        if "remove_fields" in config and isinstance(response.body, dict):
            for field_name in config["remove_fields"]:
                response.body.pop(field_name, None)
                
        return response
        
    def _mask_fields(self, response: APIResponse, config: Dict[str, Any]) -> APIResponse:
        """Маскирование полей"""
        fields = config.get("fields", [])
        mask = config.get("mask", "***")
        
        if isinstance(response.body, dict):
            for field_name in fields:
                if field_name in response.body:
                    response.body[field_name] = mask
                    
        return response


class AuthenticationManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.oauth_clients: Dict[str, OAuthClient] = {}
        self.access_tokens: Dict[str, Dict[str, Any]] = {}
        self.jwt_secret = "your-secret-key"
        
    def create_api_key(self, name: str, owner: str,
                        apis: List[str] = None,
                        scopes: List[str] = None) -> Tuple[str, APIKey]:
        """Создание API ключа"""
        raw_key = f"sk_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            key_hash=key_hash,
            name=name,
            owner=owner,
            apis=apis or [],
            scopes=scopes or []
        )
        
        self.api_keys[key_hash] = api_key
        return raw_key, api_key
        
    def validate_api_key(self, raw_key: str) -> Tuple[bool, Optional[APIKey]]:
        """Валидация API ключа"""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = self.api_keys.get(key_hash)
        
        if not api_key:
            return False, None
            
        if not api_key.enabled:
            return False, None
            
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            return False, None
            
        # Обновление статистики
        api_key.last_used_at = datetime.now()
        api_key.request_count += 1
        
        return True, api_key
        
    def create_oauth_client(self, name: str, 
                             grant_types: List[str] = None,
                             scopes: List[str] = None) -> Tuple[str, str, OAuthClient]:
        """Создание OAuth клиента"""
        client_id = f"client_{uuid.uuid4().hex[:16]}"
        client_secret = f"secret_{uuid.uuid4().hex}"
        secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
        
        client = OAuthClient(
            client_id=client_id,
            client_secret_hash=secret_hash,
            name=name,
            grant_types=grant_types or ["client_credentials"],
            scopes=scopes or []
        )
        
        self.oauth_clients[client_id] = client
        return client_id, client_secret, client
        
    def authenticate_oauth(self, client_id: str, client_secret: str,
                            grant_type: str = "client_credentials",
                            scopes: List[str] = None) -> Dict[str, Any]:
        """OAuth аутентификация"""
        client = self.oauth_clients.get(client_id)
        if not client:
            return {"error": "invalid_client", "error_description": "Client not found"}
            
        # Проверка secret
        secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
        if secret_hash != client.client_secret_hash:
            return {"error": "invalid_client", "error_description": "Invalid credentials"}
            
        if not client.enabled:
            return {"error": "invalid_client", "error_description": "Client disabled"}
            
        if grant_type not in client.grant_types:
            return {"error": "unsupported_grant_type"}
            
        # Проверка scopes
        requested_scopes = scopes or []
        if not all(s in client.scopes for s in requested_scopes):
            return {"error": "invalid_scope"}
            
        # Генерация токена
        access_token = f"at_{uuid.uuid4().hex}"
        expires_at = datetime.now() + timedelta(seconds=client.access_token_ttl)
        
        self.access_tokens[access_token] = {
            "client_id": client_id,
            "scopes": requested_scopes or client.scopes,
            "expires_at": expires_at
        }
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": client.access_token_ttl,
            "scope": " ".join(requested_scopes or client.scopes)
        }
        
    def validate_access_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Валидация access token"""
        token_data = self.access_tokens.get(token)
        
        if not token_data:
            return False, None
            
        if datetime.now() > token_data["expires_at"]:
            del self.access_tokens[token]
            return False, None
            
        return True, token_data
        
    def generate_jwt(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Генерация JWT"""
        header = {"alg": "HS256", "typ": "JWT"}
        
        payload["exp"] = int(time.time()) + expires_in
        payload["iat"] = int(time.time())
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        
        signature = hmac.new(
            self.jwt_secret.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
        
    def validate_jwt(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Валидация JWT"""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False, None
                
            header_b64, payload_b64, signature_b64 = parts
            
            # Проверка подписи
            expected_sig = hmac.new(
                self.jwt_secret.encode(),
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256
            ).digest()
            expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
            
            if signature_b64 != expected_sig_b64:
                return False, None
                
            # Декодирование payload
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            
            # Проверка срока действия
            if payload.get("exp", 0) < time.time():
                return False, None
                
            return True, payload
            
        except Exception:
            return False, None


class RateLimiter:
    """Rate Limiter"""
    
    def __init__(self, strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET):
        self.strategy = strategy
        self.buckets: Dict[str, Dict[str, Any]] = {}
        self.windows: Dict[str, Dict[str, Any]] = {}
        
    def check_rate_limit(self, key: str, limit: int, 
                          window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """Проверка rate limit"""
        if self.strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._fixed_window(key, limit, window_seconds)
        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._sliding_window(key, limit, window_seconds)
        elif self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return self._token_bucket(key, limit, window_seconds)
        else:
            return self._fixed_window(key, limit, window_seconds)
            
    def _fixed_window(self, key: str, limit: int, 
                       window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """Fixed Window"""
        current_time = time.time()
        window_key = f"{key}:{int(current_time / window_seconds)}"
        
        if window_key not in self.windows:
            self.windows[window_key] = {"count": 0, "start": current_time}
            
        window = self.windows[window_key]
        
        if window["count"] >= limit:
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset": window["start"] + window_seconds,
                "retry_after": window["start"] + window_seconds - current_time
            }
            
        window["count"] += 1
        
        return True, {
            "limit": limit,
            "remaining": limit - window["count"],
            "reset": window["start"] + window_seconds
        }
        
    def _sliding_window(self, key: str, limit: int,
                         window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """Sliding Window Log"""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        if key not in self.windows:
            self.windows[key] = {"requests": []}
            
        # Удаление старых запросов
        self.windows[key]["requests"] = [
            ts for ts in self.windows[key]["requests"]
            if ts > window_start
        ]
        
        if len(self.windows[key]["requests"]) >= limit:
            oldest = min(self.windows[key]["requests"])
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset": oldest + window_seconds,
                "retry_after": oldest + window_seconds - current_time
            }
            
        self.windows[key]["requests"].append(current_time)
        
        return True, {
            "limit": limit,
            "remaining": limit - len(self.windows[key]["requests"]),
            "reset": current_time + window_seconds
        }
        
    def _token_bucket(self, key: str, limit: int,
                       window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """Token Bucket"""
        current_time = time.time()
        refill_rate = limit / window_seconds
        
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": limit,
                "last_update": current_time
            }
            
        bucket = self.buckets[key]
        
        # Добавление токенов
        elapsed = current_time - bucket["last_update"]
        bucket["tokens"] = min(limit, bucket["tokens"] + elapsed * refill_rate)
        bucket["last_update"] = current_time
        
        if bucket["tokens"] < 1:
            return False, {
                "limit": limit,
                "remaining": 0,
                "retry_after": (1 - bucket["tokens"]) / refill_rate
            }
            
        bucket["tokens"] -= 1
        
        return True, {
            "limit": limit,
            "remaining": int(bucket["tokens"])
        }


class APICache:
    """Кэш API"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Получение из кэша"""
        entry = self.cache.get(key)
        
        if not entry:
            return None
            
        if time.time() > entry["expires_at"]:
            del self.cache[key]
            return None
            
        return entry["value"]
        
    def set(self, key: str, value: Any, ttl_seconds: int):
        """Сохранение в кэш"""
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds,
            "created_at": time.time()
        }
        
    def invalidate(self, key: str):
        """Инвалидация"""
        self.cache.pop(key, None)
        
    def invalidate_pattern(self, pattern: str):
        """Инвалидация по паттерну"""
        regex = re.compile(pattern)
        keys_to_delete = [k for k in self.cache.keys() if regex.match(k)]
        for key in keys_to_delete:
            del self.cache[key]
            
    def get_stats(self) -> Dict[str, Any]:
        """Статистика кэша"""
        current_time = time.time()
        valid_entries = [
            e for e in self.cache.values()
            if e["expires_at"] > current_time
        ]
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": len(valid_entries),
            "expired_entries": len(self.cache) - len(valid_entries)
        }


class APIAnalyticsCollector:
    """Сборщик аналитики API"""
    
    def __init__(self):
        self.requests: List[Dict[str, Any]] = []
        self.hourly_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "failed": 0,
            "latencies": []
        })
        
    def record_request(self, api_id: str, route: str, method: str,
                        status_code: int, latency_ms: float,
                        client_id: Optional[str] = None,
                        error: Optional[str] = None):
        """Запись запроса"""
        timestamp = datetime.now()
        hour_key = timestamp.strftime("%Y-%m-%d-%H")
        
        record = {
            "api_id": api_id,
            "route": route,
            "method": method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "client_id": client_id,
            "error": error,
            "timestamp": timestamp.isoformat()
        }
        
        self.requests.append(record)
        
        # Обновление hourly stats
        stats_key = f"{api_id}:{hour_key}"
        self.hourly_stats[stats_key]["total"] += 1
        if status_code < 400:
            self.hourly_stats[stats_key]["success"] += 1
        else:
            self.hourly_stats[stats_key]["failed"] += 1
        self.hourly_stats[stats_key]["latencies"].append(latency_ms)
        
    def get_analytics(self, api_id: str, 
                       hours: int = 24) -> APIAnalytics:
        """Получение аналитики"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Фильтрация запросов
        relevant_requests = [
            r for r in self.requests
            if r["api_id"] == api_id and 
            datetime.fromisoformat(r["timestamp"]) >= start_time
        ]
        
        if not relevant_requests:
            return APIAnalytics(
                api_id=api_id,
                period_start=start_time,
                period_end=end_time
            )
            
        latencies = [r["latency_ms"] for r in relevant_requests]
        latencies.sort()
        
        # Подсчёт по статусам
        status_codes = defaultdict(int)
        for r in relevant_requests:
            status_codes[r["status_code"]] += 1
            
        # Подсчёт по эндпоинтам
        endpoints = defaultdict(lambda: {"count": 0, "errors": 0})
        for r in relevant_requests:
            endpoints[r["route"]]["count"] += 1
            if r["status_code"] >= 400:
                endpoints[r["route"]]["errors"] += 1
                
        # Top клиенты
        client_counts = defaultdict(int)
        for r in relevant_requests:
            if r["client_id"]:
                client_counts[r["client_id"]] += 1
                
        top_clients = [
            {"client_id": k, "requests": v}
            for k, v in sorted(client_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return APIAnalytics(
            api_id=api_id,
            period_start=start_time,
            period_end=end_time,
            total_requests=len(relevant_requests),
            successful_requests=len([r for r in relevant_requests if r["status_code"] < 400]),
            failed_requests=len([r for r in relevant_requests if r["status_code"] >= 400]),
            avg_latency_ms=sum(latencies) / len(latencies),
            p50_latency_ms=latencies[len(latencies) // 2],
            p95_latency_ms=latencies[int(len(latencies) * 0.95)],
            p99_latency_ms=latencies[int(len(latencies) * 0.99)] if len(latencies) > 100 else latencies[-1],
            status_codes=dict(status_codes),
            endpoints=dict(endpoints),
            top_clients=top_clients
        )


class DeveloperPortal:
    """Портал разработчика"""
    
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.applications: Dict[str, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)  # app_id -> [api_ids]
        
    def register_application(self, name: str, description: str,
                              owner: str) -> Dict[str, Any]:
        """Регистрация приложения"""
        app_id = f"app_{uuid.uuid4().hex[:8]}"
        
        app = {
            "app_id": app_id,
            "name": name,
            "description": description,
            "owner": owner,
            "created_at": datetime.now().isoformat(),
            "api_keys": []
        }
        
        self.applications[app_id] = app
        return app
        
    def create_api_key_for_app(self, app_id: str, name: str) -> Dict[str, Any]:
        """Создание API ключа для приложения"""
        app = self.applications.get(app_id)
        if not app:
            return {"error": "Application not found"}
            
        raw_key, api_key = self.auth_manager.create_api_key(
            name=name,
            owner=app["owner"],
            apis=self.subscriptions.get(app_id, [])
        )
        
        app["api_keys"].append(api_key.key_id)
        
        return {
            "key_id": api_key.key_id,
            "api_key": raw_key,  # Показывается только один раз!
            "name": name,
            "created_at": api_key.created_at.isoformat()
        }
        
    def subscribe_to_api(self, app_id: str, api_id: str) -> Dict[str, Any]:
        """Подписка на API"""
        if app_id not in self.applications:
            return {"error": "Application not found"}
            
        if api_id not in self.subscriptions[app_id]:
            self.subscriptions[app_id].append(api_id)
            
        return {
            "app_id": app_id,
            "api_id": api_id,
            "subscribed": True
        }
        
    def get_api_documentation(self, api: API) -> Dict[str, Any]:
        """Получение документации API"""
        return {
            "api_id": api.api_id,
            "name": api.name,
            "version": api.version,
            "base_path": api.base_path,
            "description": api.description,
            "status": api.status.value,
            "endpoints": [
                {
                    "path": route.path,
                    "methods": [m.value for m in route.methods],
                    "description": route.description,
                    "auth_required": route.auth_required,
                    "rate_limit": route.rate_limit
                }
                for route in api.routes
            ],
            "authentication": {
                "type": api.default_auth.value,
                "description": f"Use {api.default_auth.value} authentication"
            }
        }


class APIGateway:
    """API Gateway"""
    
    def __init__(self):
        self.apis: Dict[str, API] = {}
        self.auth_manager = AuthenticationManager()
        self.rate_limiter = RateLimiter()
        self.cache = APICache()
        self.analytics = APIAnalyticsCollector()
        self.request_transformer = RequestTransformer()
        self.response_transformer = ResponseTransformer()
        self.developer_portal = DeveloperPortal(self.auth_manager)
        
    def register_api(self, api: API) -> str:
        """Регистрация API"""
        self.apis[api.api_id] = api
        return api.api_id
        
    def publish_api(self, api_id: str) -> Dict[str, Any]:
        """Публикация API"""
        api = self.apis.get(api_id)
        if not api:
            return {"error": "API not found"}
            
        api.status = APIStatus.PUBLISHED
        api.published_at = datetime.now()
        
        return {
            "api_id": api_id,
            "status": "published",
            "published_at": api.published_at.isoformat()
        }
        
    def deprecate_api(self, api_id: str, sunset_date: datetime) -> Dict[str, Any]:
        """Deprecation API"""
        api = self.apis.get(api_id)
        if not api:
            return {"error": "API not found"}
            
        api.status = APIStatus.DEPRECATED
        
        return {
            "api_id": api_id,
            "status": "deprecated",
            "sunset_date": sunset_date.isoformat()
        }
        
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """Обработка запроса"""
        start_time = time.time()
        
        # 1. Поиск API и маршрута
        api, route = self._find_route(request.path, request.method)
        
        if not api or not route:
            return APIResponse(
                status_code=404,
                headers={"Content-Type": "application/json"},
                body={"error": "Not found"},
                latency_ms=(time.time() - start_time) * 1000
            )
            
        # 2. Проверка статуса API
        if api.status == APIStatus.RETIRED:
            return APIResponse(
                status_code=410,
                headers={"Content-Type": "application/json"},
                body={"error": "API retired"},
                latency_ms=(time.time() - start_time) * 1000
            )
            
        # 3. Аутентификация
        if route.auth_required:
            auth_result = self._authenticate(request, route)
            if not auth_result["authenticated"]:
                return APIResponse(
                    status_code=401,
                    headers={"Content-Type": "application/json"},
                    body={"error": auth_result.get("error", "Unauthorized")},
                    latency_ms=(time.time() - start_time) * 1000
                )
                
        # 4. Rate Limiting
        if route.rate_limit:
            rate_key = f"{api.api_id}:{request.api_key or request.client_ip}"
            allowed, rate_info = self.rate_limiter.check_rate_limit(
                rate_key,
                route.rate_limit.get("limit", 100),
                route.rate_limit.get("window", 60)
            )
            
            if not allowed:
                response = APIResponse(
                    status_code=429,
                    headers={
                        "Content-Type": "application/json",
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(int(rate_info.get("retry_after", 60)))
                    },
                    body={"error": "Rate limit exceeded"},
                    latency_ms=(time.time() - start_time) * 1000
                )
                
                self.analytics.record_request(
                    api.api_id, route.path, request.method.value,
                    429, response.latency_ms
                )
                
                return response
                
        # 5. Проверка кэша
        if route.cache_enabled and request.method == HTTPMethod.GET:
            cache_key = f"{api.api_id}:{route.path}:{json.dumps(request.query_params, sort_keys=True)}"
            cached = self.cache.get(cache_key)
            
            if cached:
                response = APIResponse(
                    status_code=200,
                    headers={"Content-Type": "application/json", "X-Cache": "HIT"},
                    body=cached,
                    latency_ms=(time.time() - start_time) * 1000,
                    cached=True
                )
                
                self.analytics.record_request(
                    api.api_id, route.path, request.method.value,
                    200, response.latency_ms
                )
                
                return response
                
        # 6. Трансформация запроса
        if route.request_transformations:
            request = self.request_transformer.transform(request, route.request_transformations)
            
        # 7. Вызов backend
        backend_start = time.time()
        backend_response = await self._call_backend(route, request)
        backend_latency = (time.time() - backend_start) * 1000
        
        # 8. Трансформация ответа
        if route.response_transformations:
            backend_response = self.response_transformer.transform(
                backend_response, route.response_transformations
            )
            
        # 9. Кэширование
        if route.cache_enabled and request.method == HTTPMethod.GET and backend_response.status_code == 200:
            cache_key = f"{api.api_id}:{route.path}:{json.dumps(request.query_params, sort_keys=True)}"
            self.cache.set(cache_key, backend_response.body, route.cache_ttl_seconds)
            
        # 10. Добавление заголовков
        backend_response.headers["X-Request-ID"] = request.request_id
        
        if api.status == APIStatus.DEPRECATED:
            backend_response.headers["Deprecation"] = "true"
            
        # 11. Запись аналитики
        total_latency = (time.time() - start_time) * 1000
        backend_response.latency_ms = total_latency
        backend_response.backend_latency_ms = backend_latency
        
        self.analytics.record_request(
            api.api_id, route.path, request.method.value,
            backend_response.status_code, total_latency,
            client_id=request.api_key
        )
        
        return backend_response
        
    def _find_route(self, path: str, method: HTTPMethod) -> Tuple[Optional[API], Optional[APIRoute]]:
        """Поиск маршрута"""
        for api in self.apis.values():
            if api.status == APIStatus.DRAFT:
                continue
                
            if path.startswith(api.base_path):
                relative_path = path[len(api.base_path):]
                
                for route in api.routes:
                    if self._match_path(relative_path, route.path) and method in route.methods:
                        return api, route
                        
        return None, None
        
    def _match_path(self, request_path: str, route_path: str) -> bool:
        """Сопоставление пути"""
        # Простое сопоставление с параметрами
        route_parts = route_path.split("/")
        request_parts = request_path.split("/")
        
        if len(route_parts) != len(request_parts):
            return False
            
        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith("{") and route_part.endswith("}"):
                continue  # Параметр пути
            if route_part != request_part:
                return False
                
        return True
        
    def _authenticate(self, request: APIRequest, route: APIRoute) -> Dict[str, Any]:
        """Аутентификация"""
        if route.auth_type == AuthType.API_KEY:
            api_key = request.headers.get("X-API-Key") or request.api_key
            if not api_key:
                return {"authenticated": False, "error": "API key required"}
                
            valid, key_obj = self.auth_manager.validate_api_key(api_key)
            return {"authenticated": valid, "key": key_obj}
            
        elif route.auth_type == AuthType.OAUTH2 or route.auth_type == AuthType.JWT:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return {"authenticated": False, "error": "Bearer token required"}
                
            token = auth_header[7:]
            
            if route.auth_type == AuthType.OAUTH2:
                valid, token_data = self.auth_manager.validate_access_token(token)
            else:
                valid, token_data = self.auth_manager.validate_jwt(token)
                
            return {"authenticated": valid, "token_data": token_data}
            
        elif route.auth_type == AuthType.BASIC:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Basic "):
                return {"authenticated": False, "error": "Basic auth required"}
                
            # Декодирование и проверка
            return {"authenticated": True}  # Упрощённо
            
        return {"authenticated": True}
        
    async def _call_backend(self, route: APIRoute, request: APIRequest) -> APIResponse:
        """Вызов backend"""
        # Симуляция вызова backend
        await asyncio.sleep(random.uniform(0.01, 0.1))
        
        # Симуляция результата
        if random.random() < 0.95:
            return APIResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"message": "success", "data": {"id": str(uuid.uuid4())}}
            )
        else:
            return APIResponse(
                status_code=500,
                headers={"Content-Type": "application/json"},
                body={"error": "Internal server error"}
            )
            
    def get_gateway_stats(self) -> Dict[str, Any]:
        """Статистика gateway"""
        return {
            "apis": {
                "total": len(self.apis),
                "published": len([a for a in self.apis.values() if a.status == APIStatus.PUBLISHED]),
                "deprecated": len([a for a in self.apis.values() if a.status == APIStatus.DEPRECATED])
            },
            "auth": {
                "api_keys": len(self.auth_manager.api_keys),
                "oauth_clients": len(self.auth_manager.oauth_clients),
                "active_tokens": len(self.auth_manager.access_tokens)
            },
            "cache": self.cache.get_stats(),
            "portal": {
                "applications": len(self.developer_portal.applications)
            }
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 42: API Gateway")
    print("=" * 60)
    
    async def demo():
        # Создание gateway
        gateway = APIGateway()
        print("✓ API Gateway created")
        
        # Создание API
        api = API(
            api_id="api_users",
            name="User API",
            version="v1",
            base_path="/api/v1",
            description="User management API",
            default_auth=AuthType.API_KEY,
            default_rate_limit={"limit": 100, "window": 60}
        )
        
        # Добавление маршрутов
        api.routes = [
            APIRoute(
                route_id="route_list_users",
                path="/users",
                methods=[HTTPMethod.GET],
                backend_url="http://user-service:8080/users",
                rate_limit={"limit": 100, "window": 60},
                cache_enabled=True,
                cache_ttl_seconds=60,
                description="List all users"
            ),
            APIRoute(
                route_id="route_get_user",
                path="/users/{id}",
                methods=[HTTPMethod.GET],
                backend_url="http://user-service:8080/users/{id}",
                cache_enabled=True,
                cache_ttl_seconds=300,
                description="Get user by ID"
            ),
            APIRoute(
                route_id="route_create_user",
                path="/users",
                methods=[HTTPMethod.POST],
                backend_url="http://user-service:8080/users",
                request_transformations=[
                    {"type": "add_header", "name": "X-Source", "value": "api-gateway"}
                ],
                description="Create new user"
            )
        ]
        
        gateway.register_api(api)
        gateway.publish_api(api.api_id)
        print(f"✓ Registered and published API: {api.name}")
        
        # Создание API ключа
        raw_key, api_key = gateway.auth_manager.create_api_key(
            name="Test Key",
            owner="developer@example.com",
            apis=[api.api_id]
        )
        print(f"✓ Created API Key: {api_key.key_id}")
        
        # Создание OAuth клиента
        client_id, client_secret, oauth_client = gateway.auth_manager.create_oauth_client(
            name="Test App",
            grant_types=["client_credentials"],
            scopes=["read", "write"]
        )
        print(f"✓ Created OAuth Client: {client_id}")
        
        # OAuth аутентификация
        token_response = gateway.auth_manager.authenticate_oauth(
            client_id, client_secret,
            grant_type="client_credentials",
            scopes=["read"]
        )
        print(f"✓ OAuth token issued: {token_response['access_token'][:20]}...")
        
        # Симуляция запросов
        print(f"\n📊 Processing requests...")
        
        for i in range(20):
            request = APIRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                method=HTTPMethod.GET,
                path="/api/v1/users",
                headers={"X-API-Key": raw_key},
                query_params={"page": "1"},
                body=None,
                client_ip=f"192.168.1.{i % 10}"
            )
            
            response = await gateway.handle_request(request)
            
        print(f"  Processed 20 requests")
        
        # Аналитика
        analytics = gateway.analytics.get_analytics(api.api_id, hours=1)
        print(f"\n📈 API Analytics:")
        print(f"  Total Requests: {analytics.total_requests}")
        print(f"  Success: {analytics.successful_requests}")
        print(f"  Failed: {analytics.failed_requests}")
        print(f"  Avg Latency: {analytics.avg_latency_ms:.2f}ms")
        print(f"  P95 Latency: {analytics.p95_latency_ms:.2f}ms")
        
        # Developer Portal
        print(f"\n🔧 Developer Portal:")
        app = gateway.developer_portal.register_application(
            name="My App",
            description="Test application",
            owner="developer@example.com"
        )
        print(f"  Registered app: {app['app_id']}")
        
        gateway.developer_portal.subscribe_to_api(app["app_id"], api.api_id)
        print(f"  Subscribed to API: {api.api_id}")
        
        app_key = gateway.developer_portal.create_api_key_for_app(app["app_id"], "Production Key")
        print(f"  Created app key: {app_key['key_id']}")
        
        # Gateway Stats
        stats = gateway.get_gateway_stats()
        print(f"\n🎯 Gateway Stats:")
        print(f"  APIs: {stats['apis']['total']} (Published: {stats['apis']['published']})")
        print(f"  API Keys: {stats['auth']['api_keys']}")
        print(f"  OAuth Clients: {stats['auth']['oauth_clients']}")
        print(f"  Applications: {stats['portal']['applications']}")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("API Gateway initialized successfully!")
    print("=" * 60)
