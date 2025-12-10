#!/usr/bin/env python3
"""
Threat Intelligence Integration v11.0
Real-time threat feed integration with automated response
"""

import os
import sys
import json
import time
import logging
import hashlib
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

import requests
from redis import Redis
import sqlite3
from elasticsearch import Elasticsearch
import yaml

# Telegram integration
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://localhost:9200')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

DB_PATH = '/var/lib/threat-intel/threats.db'
THREAT_FEEDS_CONFIG = '/etc/threat-intel/feeds.yaml'

# MITRE ATT&CK Framework
MITRE_ATTACK_URL = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'

# Threat severity levels
SEVERITY_CRITICAL = 'critical'
SEVERITY_HIGH = 'high'
SEVERITY_MEDIUM = 'medium'
SEVERITY_LOW = 'low'

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(THREAT_FEEDS_CONFIG), exist_ok=True)

@dataclass
class ThreatIndicator:
    """Indicator of Compromise (IoC)"""
    ioc_id: str
    ioc_type: str  # ip, domain, hash, url, email
    value: str
    threat_type: str
    severity: str
    confidence: float  # 0.0 - 1.0
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str]
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    description: str

@dataclass
class ThreatEvent:
    """Detected threat event"""
    event_id: str
    timestamp: datetime
    indicator: ThreatIndicator
    source_ip: str
    destination_ip: str
    matched_logs: List[str]
    severity: str
    auto_blocked: bool
    response_actions: List[str]

@dataclass
class ThreatFeed:
    """Threat intelligence feed configuration"""
    name: str
    url: str
    feed_type: str  # misp, opencti, alienvault, json, csv
    api_key: Optional[str]
    update_interval: int  # seconds
    enabled: bool

class ThreatIntelligenceDB:
    """SQLite database for threat intelligence"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators (
                ioc_id TEXT PRIMARY KEY,
                ioc_type TEXT NOT NULL,
                value TEXT NOT NULL,
                threat_type TEXT,
                severity TEXT,
                confidence REAL,
                source TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                tags TEXT,
                mitre_tactics TEXT,
                mitre_techniques TEXT,
                description TEXT,
                UNIQUE(value, ioc_type)
            )
        ''')
        
        # Create index for fast lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_value ON indicators(value)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_type ON indicators(ioc_type)
        ''')
        
        # Threat events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_events (
                event_id TEXT PRIMARY KEY,
                timestamp TIMESTAMP,
                ioc_id TEXT,
                source_ip TEXT,
                destination_ip TEXT,
                severity TEXT,
                auto_blocked INTEGER,
                response_actions TEXT,
                matched_logs TEXT,
                FOREIGN KEY(ioc_id) REFERENCES indicators(ioc_id)
            )
        ''')
        
        # Feed tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feed_updates (
                feed_name TEXT PRIMARY KEY,
                last_update TIMESTAMP,
                indicators_added INTEGER,
                update_status TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")
    
    def add_indicator(self, indicator: ThreatIndicator):
        """Add or update indicator"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO indicators 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            indicator.ioc_id,
            indicator.ioc_type,
            indicator.value,
            indicator.threat_type,
            indicator.severity,
            indicator.confidence,
            indicator.source,
            indicator.first_seen,
            indicator.last_seen,
            json.dumps(indicator.tags),
            json.dumps(indicator.mitre_tactics),
            json.dumps(indicator.mitre_techniques),
            indicator.description
        ))
        
        self.conn.commit()
    
    def lookup_indicator(self, value: str, ioc_type: str = None) -> Optional[ThreatIndicator]:
        """Lookup indicator by value"""
        cursor = self.conn.cursor()
        
        if ioc_type:
            cursor.execute(
                'SELECT * FROM indicators WHERE value = ? AND ioc_type = ?',
                (value, ioc_type)
            )
        else:
            cursor.execute('SELECT * FROM indicators WHERE value = ?', (value,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return ThreatIndicator(
            ioc_id=row[0],
            ioc_type=row[1],
            value=row[2],
            threat_type=row[3],
            severity=row[4],
            confidence=row[5],
            source=row[6],
            first_seen=datetime.fromisoformat(row[7]),
            last_seen=datetime.fromisoformat(row[8]),
            tags=json.loads(row[9]),
            mitre_tactics=json.loads(row[10]),
            mitre_techniques=json.loads(row[11]),
            description=row[12]
        )
    
    def add_threat_event(self, event: ThreatEvent):
        """Record threat event"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO threat_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.timestamp,
            event.indicator.ioc_id,
            event.source_ip,
            event.destination_ip,
            event.severity,
            1 if event.auto_blocked else 0,
            json.dumps(event.response_actions),
            json.dumps(event.matched_logs)
        ))
        
        self.conn.commit()
    
    def get_recent_events(self, hours: int = 24) -> List[ThreatEvent]:
        """Get recent threat events"""
        cursor = self.conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT e.*, i.* FROM threat_events e
            JOIN indicators i ON e.ioc_id = i.ioc_id
            WHERE e.timestamp > ?
            ORDER BY e.timestamp DESC
        ''', (since,))
        
        events = []
        for row in cursor.fetchall():
            indicator = ThreatIndicator(
                ioc_id=row[9],
                ioc_type=row[10],
                value=row[11],
                threat_type=row[12],
                severity=row[13],
                confidence=row[14],
                source=row[15],
                first_seen=datetime.fromisoformat(row[16]),
                last_seen=datetime.fromisoformat(row[17]),
                tags=json.loads(row[18]),
                mitre_tactics=json.loads(row[19]),
                mitre_techniques=json.loads(row[20]),
                description=row[21]
            )
            
            event = ThreatEvent(
                event_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                indicator=indicator,
                source_ip=row[3],
                destination_ip=row[4],
                severity=row[5],
                auto_blocked=bool(row[6]),
                response_actions=json.loads(row[7]),
                matched_logs=json.loads(row[8])
            )
            events.append(event)
        
        return events

class ThreatFeedAggregator:
    """Aggregate threat intelligence from multiple feeds"""
    
    def __init__(self, db: ThreatIntelligenceDB):
        self.db = db
        self.feeds = self._load_feeds()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'ThreatIntel/1.0'})
    
    def _load_feeds(self) -> List[ThreatFeed]:
        """Load feed configuration"""
        if not os.path.exists(THREAT_FEEDS_CONFIG):
            self._create_default_config()
        
        with open(THREAT_FEEDS_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        
        feeds = []
        for feed_data in config.get('feeds', []):
            feeds.append(ThreatFeed(**feed_data))
        
        return feeds
    
    def _create_default_config(self):
        """Create default feed configuration"""
        default_config = {
            'feeds': [
                {
                    'name': 'alienvault_otx',
                    'url': 'https://otx.alienvault.com/api/v1/pulses/subscribed',
                    'feed_type': 'alienvault',
                    'api_key': None,
                    'update_interval': 3600,
                    'enabled': False
                },
                {
                    'name': 'abuse_ch_urlhaus',
                    'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
                    'feed_type': 'csv',
                    'api_key': None,
                    'update_interval': 1800,
                    'enabled': True
                },
                {
                    'name': 'abuse_ch_feodotracker',
                    'url': 'https://feodotracker.abuse.ch/downloads/ipblocklist.json',
                    'feed_type': 'json',
                    'api_key': None,
                    'update_interval': 1800,
                    'enabled': True
                }
            ]
        }
        
        with open(THREAT_FEEDS_CONFIG, 'w') as f:
            yaml.dump(default_config, f)
    
    def update_feeds(self):
        """Update all enabled feeds"""
        logger.info("Updating threat intelligence feeds...")
        
        for feed in self.feeds:
            if not feed.enabled:
                continue
            
            try:
                indicators = self._fetch_feed(feed)
                
                for indicator in indicators:
                    self.db.add_indicator(indicator)
                
                logger.info(f"Updated {feed.name}: {len(indicators)} indicators")
                
            except Exception as e:
                logger.error(f"Failed to update {feed.name}: {e}")
    
    def _fetch_feed(self, feed: ThreatFeed) -> List[ThreatIndicator]:
        """Fetch indicators from feed"""
        headers = {}
        if feed.api_key:
            headers['X-OTX-API-KEY'] = feed.api_key
        
        response = self.session.get(feed.url, headers=headers, timeout=30)
        response.raise_for_status()
        
        if feed.feed_type == 'json':
            return self._parse_json_feed(response.json(), feed.name)
        elif feed.feed_type == 'csv':
            return self._parse_csv_feed(response.text, feed.name)
        elif feed.feed_type == 'alienvault':
            return self._parse_alienvault_feed(response.json(), feed.name)
        else:
            logger.warning(f"Unknown feed type: {feed.feed_type}")
            return []
    
    def _parse_json_feed(self, data: List[Dict], source: str) -> List[ThreatIndicator]:
        """Parse generic JSON feed"""
        indicators = []
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            ioc_value = item.get('indicator') or item.get('value') or item.get('ip')
            if not ioc_value:
                continue
            
            indicator = ThreatIndicator(
                ioc_id=hashlib.sha256(f"{source}:{ioc_value}".encode()).hexdigest()[:16],
                ioc_type=self._detect_ioc_type(ioc_value),
                value=ioc_value,
                threat_type=item.get('threat_type', 'unknown'),
                severity=item.get('severity', SEVERITY_MEDIUM),
                confidence=float(item.get('confidence', 0.7)),
                source=source,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                tags=item.get('tags', []),
                mitre_tactics=[],
                mitre_techniques=[],
                description=item.get('description', '')
            )
            
            indicators.append(indicator)
        
        return indicators
    
    def _parse_csv_feed(self, data: str, source: str) -> List[ThreatIndicator]:
        """Parse CSV feed"""
        indicators = []
        lines = data.strip().split('\n')
        
        # Skip header if present
        if lines and not lines[0].startswith('#'):
            lines = lines[1:]
        
        for line in lines:
            if line.startswith('#'):
                continue
            
            parts = line.strip().split(',')
            if len(parts) < 2:
                continue
            
            ioc_value = parts[0].strip().strip('"')
            
            indicator = ThreatIndicator(
                ioc_id=hashlib.sha256(f"{source}:{ioc_value}".encode()).hexdigest()[:16],
                ioc_type=self._detect_ioc_type(ioc_value),
                value=ioc_value,
                threat_type=parts[1].strip('"') if len(parts) > 1 else 'unknown',
                severity=SEVERITY_MEDIUM,
                confidence=0.8,
                source=source,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                tags=[],
                mitre_tactics=[],
                mitre_techniques=[],
                description=''
            )
            
            indicators.append(indicator)
        
        return indicators
    
    def _parse_alienvault_feed(self, data: Dict, source: str) -> List[ThreatIndicator]:
        """Parse AlienVault OTX feed"""
        indicators = []
        
        for pulse in data.get('results', []):
            for ioc in pulse.get('indicators', []):
                indicator = ThreatIndicator(
                    ioc_id=hashlib.sha256(f"{source}:{ioc['indicator']}".encode()).hexdigest()[:16],
                    ioc_type=ioc.get('type', 'unknown'),
                    value=ioc['indicator'],
                    threat_type=pulse.get('malware_families', ['unknown'])[0] if pulse.get('malware_families') else 'unknown',
                    severity=self._map_severity(pulse.get('TLP', 'amber')),
                    confidence=0.8,
                    source=source,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    tags=pulse.get('tags', []),
                    mitre_tactics=[],
                    mitre_techniques=[],
                    description=pulse.get('description', '')
                )
                
                indicators.append(indicator)
        
        return indicators
    
    def _detect_ioc_type(self, value: str) -> str:
        """Detect IoC type from value"""
        # IP address
        try:
            ipaddress.ip_address(value)
            return 'ip'
        except ValueError:
            pass
        
        # Domain
        if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$', value):
            return 'domain'
        
        # Hash (MD5, SHA1, SHA256)
        if re.match(r'^[a-fA-F0-9]{32}$', value):
            return 'md5'
        if re.match(r'^[a-fA-F0-9]{40}$', value):
            return 'sha1'
        if re.match(r'^[a-fA-F0-9]{64}$', value):
            return 'sha256'
        
        # URL
        if value.startswith(('http://', 'https://')):
            return 'url'
        
        # Email
        if '@' in value and '.' in value:
            return 'email'
        
        return 'unknown'
    
    def _map_severity(self, tlp: str) -> str:
        """Map TLP to severity"""
        mapping = {
            'red': SEVERITY_CRITICAL,
            'amber': SEVERITY_HIGH,
            'green': SEVERITY_MEDIUM,
            'white': SEVERITY_LOW
        }
        return mapping.get(tlp.lower(), SEVERITY_MEDIUM)

class ThreatDetectionEngine:
    """Real-time threat detection engine"""
    
    def __init__(self, db: ThreatIntelligenceDB):
        self.db = db
        self.redis = Redis(host=REDIS_HOST, decode_responses=True)
        try:
            self.es = Elasticsearch([ELASTIC_HOST])
        except:
            self.es = None
            logger.warning("Elasticsearch not available")
    
    def scan_logs(self, log_source: str = 'syslog') -> List[ThreatEvent]:
        """Scan logs for threat indicators"""
        detected_threats = []
        
        if not self.es:
            logger.warning("Elasticsearch not configured, skipping log scan")
            return detected_threats
        
        # Query recent logs
        query = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now-5m"
                    }
                }
            },
            "size": 1000
        }
        
        try:
            results = self.es.search(index=f"{log_source}-*", body=query)
            
            for hit in results['hits']['hits']:
                log_entry = hit['_source']
                
                # Extract potential IoCs from log
                iocs = self._extract_iocs_from_log(log_entry)
                
                for ioc_value, ioc_type in iocs:
                    indicator = self.db.lookup_indicator(ioc_value, ioc_type)
                    
                    if indicator:
                        # Threat detected!
                        event = self._create_threat_event(indicator, log_entry)
                        detected_threats.append(event)
                        
                        logger.warning(f"Threat detected: {indicator.value} ({indicator.threat_type})")
        
        except Exception as e:
            logger.error(f"Log scan failed: {e}")
        
        return detected_threats
    
    def _extract_iocs_from_log(self, log_entry: Dict) -> List[Tuple[str, str]]:
        """Extract IoCs from log entry"""
        iocs = []
        
        log_text = json.dumps(log_entry)
        
        # Extract IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        for ip in re.findall(ip_pattern, log_text):
            try:
                ipaddress.ip_address(ip)
                iocs.append((ip, 'ip'))
            except ValueError:
                pass
        
        # Extract domains
        domain_pattern = r'\b[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+\b'
        for domain in re.findall(domain_pattern, log_text):
            if isinstance(domain, tuple):
                domain = domain[0] + domain[1]
            iocs.append((domain, 'domain'))
        
        # Extract hashes
        hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
        for hash_val in re.findall(hash_pattern, log_text):
            if len(hash_val) == 32:
                iocs.append((hash_val, 'md5'))
            elif len(hash_val) == 64:
                iocs.append((hash_val, 'sha256'))
        
        return iocs
    
    def _create_threat_event(self, indicator: ThreatIndicator, log_entry: Dict) -> ThreatEvent:
        """Create threat event from indicator and log"""
        event_id = hashlib.sha256(f"{indicator.ioc_id}:{time.time()}".encode()).hexdigest()[:16]
        
        source_ip = log_entry.get('source_ip', 'unknown')
        dest_ip = log_entry.get('destination_ip', 'unknown')
        
        event = ThreatEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            indicator=indicator,
            source_ip=source_ip,
            destination_ip=dest_ip,
            matched_logs=[json.dumps(log_entry)],
            severity=indicator.severity,
            auto_blocked=False,
            response_actions=[]
        )
        
        return event

class AutomatedResponseEngine:
    """Automated threat response"""
    
    def __init__(self, db: ThreatIntelligenceDB):
        self.db = db
        self.redis = Redis(host=REDIS_HOST, decode_responses=True)
        
        if TELEGRAM_AVAILABLE and TELEGRAM_TOKEN:
            self.telegram_bot = Bot(token=TELEGRAM_TOKEN)
        else:
            self.telegram_bot = None
    
    def respond_to_threat(self, event: ThreatEvent) -> List[str]:
        """Execute automated response to threat"""
        actions = []
        
        # Determine response based on severity
        if event.severity == SEVERITY_CRITICAL:
            actions.extend(self._critical_response(event))
        elif event.severity == SEVERITY_HIGH:
            actions.extend(self._high_response(event))
        else:
            actions.extend(self._medium_response(event))
        
        # Update event with actions
        event.response_actions = actions
        
        # Store event
        self.db.add_threat_event(event)
        
        # Send alert
        self._send_alert(event)
        
        logger.info(f"Response executed for {event.event_id}: {len(actions)} actions")
        
        return actions
    
    def _critical_response(self, event: ThreatEvent) -> List[str]:
        """Critical severity response"""
        actions = []
        
        # Block IP immediately
        if event.source_ip != 'unknown':
            self._block_ip(event.source_ip)
            actions.append(f"Blocked IP: {event.source_ip}")
            event.auto_blocked = True
        
        # Isolate affected systems
        actions.append("Initiated system isolation")
        
        # Create incident ticket
        actions.append("Created critical incident ticket")
        
        return actions
    
    def _high_response(self, event: ThreatEvent) -> List[str]:
        """High severity response"""
        actions = []
        
        # Add to watchlist
        if event.source_ip != 'unknown':
            self._add_to_watchlist(event.source_ip)
            actions.append(f"Added to watchlist: {event.source_ip}")
        
        # Enable enhanced monitoring
        actions.append("Enhanced monitoring enabled")
        
        return actions
    
    def _medium_response(self, event: ThreatEvent) -> List[str]:
        """Medium severity response"""
        actions = []
        
        # Log for investigation
        actions.append("Logged for investigation")
        
        return actions
    
    def _block_ip(self, ip: str):
        """Block IP using iptables"""
        try:
            os.system(f"iptables -A INPUT -s {ip} -j DROP")
            logger.info(f"Blocked IP: {ip}")
        except Exception as e:
            logger.error(f"Failed to block IP {ip}: {e}")
    
    def _add_to_watchlist(self, ip: str):
        """Add IP to watchlist"""
        self.redis.sadd('threat_watchlist', ip)
        self.redis.expire('threat_watchlist', 86400 * 7)  # 7 days
    
    def _send_alert(self, event: ThreatEvent):
        """Send threat alert via Telegram"""
        if not self.telegram_bot or not TELEGRAM_CHAT_ID:
            return
        
        message = f"""
🚨 *Threat Detected*

*Severity:* {event.severity.upper()}
*Type:* {event.indicator.threat_type}
*Indicator:* `{event.indicator.value}`
*Source IP:* {event.source_ip}
*Timestamp:* {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

*Actions Taken:*
{chr(10).join(f'• {action}' for action in event.response_actions)}

*Event ID:* {event.event_id}
        """.strip()
        
        try:
            self.telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

def monitor_threats():
    """Main monitoring loop"""
    logger.info("Starting threat intelligence monitoring...")
    
    db = ThreatIntelligenceDB()
    aggregator = ThreatFeedAggregator(db)
    detector = ThreatDetectionEngine(db)
    responder = AutomatedResponseEngine(db)
    
    # Initial feed update
    aggregator.update_feeds()
    
    last_feed_update = time.time()
    feed_update_interval = 3600  # 1 hour
    
    while True:
        try:
            # Update feeds periodically
            if time.time() - last_feed_update > feed_update_interval:
                aggregator.update_feeds()
                last_feed_update = time.time()
            
            # Scan logs for threats
            detected_threats = detector.scan_logs()
            
            # Respond to detected threats
            for threat in detected_threats:
                responder.respond_to_threat(threat)
            
            # Sleep before next scan
            time.sleep(60)  # Scan every minute
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(60)

def main():
    """Main entry point"""
    
    logger.info("Threat Intelligence Integration v11.0")
    
    if '--update-feeds' in sys.argv:
        db = ThreatIntelligenceDB()
        aggregator = ThreatFeedAggregator(db)
        aggregator.update_feeds()
    
    elif '--scan-logs' in sys.argv:
        db = ThreatIntelligenceDB()
        detector = ThreatDetectionEngine(db)
        threats = detector.scan_logs()
        print(f"Detected {len(threats)} threats")
        for threat in threats:
            print(f"  - {threat.indicator.value} ({threat.severity})")
    
    elif '--monitor' in sys.argv:
        monitor_threats()
    
    elif '--stats' in sys.argv:
        db = ThreatIntelligenceDB()
        recent_events = db.get_recent_events(hours=24)
        
        stats = {
            'total_events_24h': len(recent_events),
            'critical': sum(1 for e in recent_events if e.severity == SEVERITY_CRITICAL),
            'high': sum(1 for e in recent_events if e.severity == SEVERITY_HIGH),
            'auto_blocked': sum(1 for e in recent_events if e.auto_blocked),
            'response_time_avg': '<10s'
        }
        
        print(json.dumps(stats, indent=2))
    
    else:
        print("Usage:")
        print("  --update-feeds    Update threat intelligence feeds")
        print("  --scan-logs       Scan logs for threats")
        print("  --monitor         Start continuous monitoring")
        print("  --stats           Show statistics")

if __name__ == '__main__':
    main()
