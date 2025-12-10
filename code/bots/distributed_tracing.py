#!/usr/bin/env python3
"""
Distributed Tracing System v13.0
OpenTelemetry + Jaeger for end-to-end tracing
Complete observability with context propagation
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from contextlib import contextmanager
import functools

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.trace import Status, StatusCode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
JAEGER_HOST = os.getenv('JAEGER_HOST', 'localhost')
JAEGER_PORT = int(os.getenv('JAEGER_PORT', '6831'))
SERVICE_NAME_VALUE = os.getenv('SERVICE_NAME', 'server-init')

################################################################################
# Tracer Setup
################################################################################

class DistributedTracer:
    """Distributed tracing manager"""
    
    def __init__(self, service_name: str = SERVICE_NAME_VALUE):
        self.service_name = service_name
        self.tracer_provider = None
        self.tracer = None
        
        self._init_tracer()
    
    def _init_tracer(self):
        """Initialize OpenTelemetry tracer"""
        
        # Create resource
        resource = Resource(attributes={
            SERVICE_NAME: self.service_name
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Create Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=JAEGER_HOST,
            agent_port=JAEGER_PORT,
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        self.tracer_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        # Instrument libraries
        RequestsInstrumentor().instrument()
        
        logger.info(f"Distributed tracing initialized: {self.service_name}")
    
    @contextmanager
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a new span"""
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise
    
    def trace_function(self, func_name: Optional[str] = None):
        """Decorator to trace function"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                with self.start_span(name) as span:
                    span.set_attribute("function", func.__name__)
                    result = func(*args, **kwargs)
                    return result
            
            return wrapper
        return decorator
    
    def add_event(self, name: str, attributes: Optional[Dict] = None):
        """Add event to current span"""
        span = trace.get_current_span()
        if span:
            span.add_event(name, attributes=attributes or {})

# Global tracer instance
tracer = DistributedTracer()

################################################################################
# Tracing Decorators
################################################################################

def trace_operation(operation_name: str):
    """Decorator for tracing operations"""
    return tracer.trace_function(operation_name)

################################################################################
# Example Integration
################################################################################

@trace_operation("deployment.create")
def create_deployment(name: str, replicas: int):
    """Example traced function"""
    tracer.add_event("deployment.validation", {"name": name, "replicas": replicas})
    
    # Simulate work
    import time
    time.sleep(0.1)
    
    tracer.add_event("deployment.created", {"deployment_id": "deploy-123"})
    
    return {"deployment_id": "deploy-123", "status": "created"}

@trace_operation("security.scan")
def security_scan(target: str):
    """Example security scan with tracing"""
    with tracer.start_span("security.scan.prepare") as span:
        span.set_attribute("target", target)
    
    with tracer.start_span("security.scan.execute"):
        import time
        time.sleep(0.2)
    
    return {"threats_found": 0}

################################################################################
# CLI
################################################################################

def main():
    """Main entry point"""
    logger.info("Distributed Tracing System v13.0")
    
    if '--test' in sys.argv:
        print("Testing distributed tracing...")
        
        # Test operations
        result1 = create_deployment("web-app", 3)
        print(f"Deployment: {result1}")
        
        result2 = security_scan("192.168.1.0/24")
        print(f"Security scan: {result2}")
        
        print("✅ Traces sent to Jaeger")
        print(f"View at: http://{JAEGER_HOST}:16686")
    
    else:
        print(f"""
Distributed Tracing System v13.0

Configuration:
  Service: {SERVICE_NAME_VALUE}
  Jaeger: {JAEGER_HOST}:{JAEGER_PORT}
  UI: http://{JAEGER_HOST}:16686

Usage:
  --test    Run test traces

Example:
  python3 distributed_tracing.py --test
        """)

if __name__ == '__main__':
    main()
