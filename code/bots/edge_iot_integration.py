#!/usr/bin/env python3
"""
Edge Computing & IoT Integration v11.0
Edge node orchestration, device management, data aggregation
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3

import paho.mqtt.client as mqtt
import redis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DB_PATH = '/var/lib/edge/devices.db'
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

@dataclass
class EdgeNode:
    """Edge computing node"""
    node_id: str
    location: str
    capacity_cpu: float
    capacity_memory: float
    status: str
    latency_ms: float

@dataclass
class IoTDevice:
    """IoT device"""
    device_id: str
    device_type: str
    edge_node_id: str
    status: str
    last_seen: datetime
    firmware_version: str

class EdgeDatabase:
    """SQLite database for edge/IoT data"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edge_nodes (
                node_id TEXT PRIMARY KEY,
                location TEXT NOT NULL,
                capacity_cpu REAL,
                capacity_memory REAL,
                status TEXT DEFAULT 'active',
                latency_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iot_devices (
                device_id TEXT PRIMARY KEY,
                device_type TEXT NOT NULL,
                edge_node_id TEXT,
                status TEXT DEFAULT 'online',
                last_seen TIMESTAMP,
                firmware_version TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(edge_node_id) REFERENCES edge_nodes(node_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_telemetry (
                telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(device_id) REFERENCES iot_devices(device_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS edge_workloads (
                workload_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workload_name TEXT NOT NULL,
                edge_node_id TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                status TEXT DEFAULT 'running',
                deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(edge_node_id) REFERENCES edge_nodes(node_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_telemetry_device ON device_telemetry(device_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_node ON iot_devices(edge_node_id)')
        
        self.conn.commit()
        logger.info(f"Edge database initialized: {self.db_path}")
    
    def register_edge_node(self, node: EdgeNode):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO edge_nodes (node_id, location, capacity_cpu, capacity_memory, status, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node.node_id, node.location, node.capacity_cpu, node.capacity_memory, node.status, node.latency_ms))
        self.conn.commit()
    
    def register_device(self, device: IoTDevice):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO iot_devices (device_id, device_type, edge_node_id, status, last_seen, firmware_version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (device.device_id, device.device_type, device.edge_node_id, device.status, device.last_seen, device.firmware_version))
        self.conn.commit()
    
    def record_telemetry(self, device_id: str, metric_name: str, metric_value: float):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO device_telemetry (device_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (device_id, metric_name, metric_value))
        self.conn.commit()

class EdgeOrchestrator:
    """Edge node orchestration"""
    
    def __init__(self, db: EdgeDatabase):
        self.db = db
        self.redis = redis.Redis(host=REDIS_HOST, decode_responses=True)
    
    def select_optimal_edge_node(self, required_cpu: float, required_memory: float, preferred_location: str = None) -> Optional[str]:
        """Select optimal edge node for workload placement"""
        
        cursor = self.db.conn.cursor()
        
        if preferred_location:
            cursor.execute('''
                SELECT node_id, latency_ms, capacity_cpu, capacity_memory
                FROM edge_nodes
                WHERE status = 'active' AND location = ? AND capacity_cpu >= ? AND capacity_memory >= ?
                ORDER BY latency_ms ASC
                LIMIT 1
            ''', (preferred_location, required_cpu, required_memory))
        else:
            cursor.execute('''
                SELECT node_id, latency_ms, capacity_cpu, capacity_memory
                FROM edge_nodes
                WHERE status = 'active' AND capacity_cpu >= ? AND capacity_memory >= ?
                ORDER BY latency_ms ASC
                LIMIT 1
            ''', (required_cpu, required_memory))
        
        row = cursor.fetchone()
        if row:
            logger.info(f"Selected edge node: {row[0]} (latency: {row[1]}ms)")
            return row[0]
        
        return None
    
    def deploy_workload(self, workload_name: str, cpu: float, memory: float, location: str = None) -> bool:
        """Deploy workload to optimal edge node"""
        
        node_id = self.select_optimal_edge_node(cpu, memory, location)
        
        if not node_id:
            logger.error("No suitable edge node found")
            return False
        
        # Deploy workload (simplified)
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT INTO edge_workloads (workload_name, edge_node_id, cpu_usage, memory_usage, status)
            VALUES (?, ?, ?, ?, 'running')
        ''', (workload_name, node_id, cpu, memory))
        self.db.conn.commit()
        
        logger.info(f"Deployed {workload_name} to edge node {node_id}")
        return True
    
    def check_node_health(self) -> Dict:
        """Check health of all edge nodes"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT node_id, location, status, latency_ms FROM edge_nodes')
        
        nodes = []
        for row in cursor.fetchall():
            nodes.append({
                'node_id': row[0],
                'location': row[1],
                'status': row[2],
                'latency_ms': row[3]
            })
        
        healthy_count = sum(1 for n in nodes if n['status'] == 'active')
        
        return {
            'total_nodes': len(nodes),
            'healthy_nodes': healthy_count,
            'nodes': nodes
        }

class IoTManager:
    """IoT device management"""
    
    def __init__(self, db: EdgeDatabase):
        self.db = db
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
    
    def start_mqtt_broker(self):
        """Start MQTT broker connection"""
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT connected with result code {rc}")
        client.subscribe("devices/+/telemetry")
        client.subscribe("devices/+/status")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[1]
        message_type = topic_parts[2]
        
        try:
            payload = json.loads(msg.payload.decode())
            
            if message_type == 'telemetry':
                self._handle_telemetry(device_id, payload)
            elif message_type == 'status':
                self._handle_status(device_id, payload)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _handle_telemetry(self, device_id: str, payload: Dict):
        """Handle device telemetry data"""
        
        for metric_name, metric_value in payload.items():
            self.db.record_telemetry(device_id, metric_name, float(metric_value))
        
        # Update last_seen
        cursor = self.db.conn.cursor()
        cursor.execute('UPDATE iot_devices SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?', (device_id,))
        self.db.conn.commit()
    
    def _handle_status(self, device_id: str, payload: Dict):
        """Handle device status update"""
        
        status = payload.get('status', 'unknown')
        
        cursor = self.db.conn.cursor()
        cursor.execute('UPDATE iot_devices SET status = ?, last_seen = CURRENT_TIMESTAMP WHERE device_id = ?', (status, device_id))
        self.db.conn.commit()
        
        logger.info(f"Device {device_id} status: {status}")
    
    def get_device_count(self) -> int:
        """Get total device count"""
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM iot_devices')
        return cursor.fetchone()[0]
    
    def get_online_devices(self) -> List[Dict]:
        """Get list of online devices"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT device_id, device_type, edge_node_id, last_seen
            FROM iot_devices
            WHERE status = 'online' AND last_seen > datetime('now', '-5 minutes')
        ''')
        
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'device_id': row[0],
                'device_type': row[1],
                'edge_node_id': row[2],
                'last_seen': row[3]
            })
        return devices

class DataAggregator:
    """Aggregate data from edge nodes"""
    
    def __init__(self, db: EdgeDatabase):
        self.db = db
    
    def aggregate_telemetry(self, device_id: str, metric_name: str, hours: int = 1) -> Dict:
        """Aggregate telemetry data"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(metric_value) as avg_value,
                MIN(metric_value) as min_value,
                MAX(metric_value) as max_value,
                COUNT(*) as sample_count
            FROM device_telemetry
            WHERE device_id = ? AND metric_name = ? AND timestamp > datetime('now', ? || ' hours')
        ''', (device_id, metric_name, -hours))
        
        row = cursor.fetchone()
        if row:
            return {
                'device_id': device_id,
                'metric_name': metric_name,
                'avg': row[0],
                'min': row[1],
                'max': row[2],
                'sample_count': row[3],
                'period_hours': hours
            }
        return {}

class EdgeIoTSystem:
    """Main edge computing & IoT system"""
    
    def __init__(self):
        self.db = EdgeDatabase()
        self.orchestrator = EdgeOrchestrator(self.db)
        self.iot_manager = IoTManager(self.db)
        self.aggregator = DataAggregator(self.db)
    
    def start(self):
        """Start the system"""
        logger.info("Starting Edge Computing & IoT System v11.0")
        self.iot_manager.start_mqtt_broker()
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        
        edge_health = self.orchestrator.check_node_health()
        device_count = self.iot_manager.get_device_count()
        online_devices = len(self.iot_manager.get_online_devices())
        
        return {
            'edge_nodes': edge_health,
            'total_devices': device_count,
            'online_devices': online_devices,
            'device_connectivity': f"{online_devices}/{device_count}" if device_count > 0 else "0/0"
        }

def main():
    """Main entry point"""
    
    system = EdgeIoTSystem()
    
    if '--start' in sys.argv:
        system.start()
        logger.info("System started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            
    elif '--status' in sys.argv:
        status = system.get_system_status()
        print(json.dumps(status, indent=2))
        
    elif '--register-node' in sys.argv:
        node = EdgeNode(
            node_id=sys.argv[2],
            location=sys.argv[3],
            capacity_cpu=float(sys.argv[4]),
            capacity_memory=float(sys.argv[5]),
            status='active',
            latency_ms=float(sys.argv[6])
        )
        system.db.register_edge_node(node)
        logger.info(f"Edge node registered: {node.node_id}")
        
    elif '--register-device' in sys.argv:
        device = IoTDevice(
            device_id=sys.argv[2],
            device_type=sys.argv[3],
            edge_node_id=sys.argv[4],
            status='online',
            last_seen=datetime.now(),
            firmware_version=sys.argv[5]
        )
        system.db.register_device(device)
        logger.info(f"Device registered: {device.device_id}")
        
    else:
        print("Edge Computing & IoT Integration v11.0")
        print("")
        print("Usage:")
        print("  --start                                   Start system")
        print("  --status                                  System status")
        print("  --register-node ID LOC CPU MEM LATENCY    Register edge node")
        print("  --register-device ID TYPE NODE FW         Register IoT device")

if __name__ == '__main__':
    main()
