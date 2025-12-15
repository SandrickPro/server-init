#!/usr/bin/env python3
"""
Server Init - Iteration 316: DNS Manager Platform
Платформа управления DNS

Функционал:
- Zone Management - управление зонами
- Record Management - управление записями
- DNSSEC - расширения безопасности
- Dynamic DNS - динамический DNS
- DNS Forwarding - пересылка DNS
- Monitoring - мониторинг
- Import/Export - импорт/экспорт
- Analytics - аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class RecordType(Enum):
    """Тип DNS записи"""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SOA = "SOA"
    PTR = "PTR"
    SRV = "SRV"
    CAA = "CAA"


class ZoneType(Enum):
    """Тип зоны"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    FORWARD = "forward"
    STUB = "stub"


class ZoneStatus(Enum):
    """Статус зоны"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"


class DNSSECStatus(Enum):
    """Статус DNSSEC"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    PENDING = "pending"


@dataclass
class DNSRecord:
    """DNS запись"""
    record_id: str
    zone_id: str
    
    # Record
    name: str = ""
    record_type: RecordType = RecordType.A
    value: str = ""
    
    # TTL
    ttl: int = 3600  # seconds
    
    # Priority (for MX, SRV)
    priority: int = 0
    
    # Weight & Port (for SRV)
    weight: int = 0
    port: int = 0
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Stats
    query_count: int = 0


@dataclass
class Zone:
    """DNS зона"""
    zone_id: str
    name: str
    
    # Type
    zone_type: ZoneType = ZoneType.PRIMARY
    
    # Status
    status: ZoneStatus = ZoneStatus.ACTIVE
    
    # SOA
    primary_ns: str = "ns1.example.com"
    admin_email: str = "admin.example.com"  # @ replaced with .
    serial: int = 1
    refresh: int = 3600
    retry: int = 600
    expire: int = 86400
    minimum_ttl: int = 60
    
    # DNSSEC
    dnssec_status: DNSSECStatus = DNSSECStatus.DISABLED
    
    # Records
    records: List[str] = field(default_factory=list)  # record_ids
    
    # Transfer
    allow_transfer: List[str] = field(default_factory=list)  # IP addresses
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Stats
    total_queries: int = 0


@dataclass
class Forwarder:
    """DNS форвардер"""
    forwarder_id: str
    name: str
    
    # Address
    address: str = ""
    port: int = 53
    
    # Domains
    domains: List[str] = field(default_factory=list)  # empty = all domains
    
    # Priority
    priority: int = 0
    
    # Status
    is_active: bool = True
    is_healthy: bool = True


@dataclass
class DNSQuery:
    """DNS запрос"""
    query_id: str
    zone_id: str
    
    # Query
    name: str = ""
    query_type: RecordType = RecordType.A
    
    # Client
    client_ip: str = ""
    
    # Result
    response_code: str = "NOERROR"  # NOERROR, NXDOMAIN, SERVFAIL, etc.
    answer_count: int = 0
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_ms: float = 0


@dataclass
class DNSSECKey:
    """DNSSEC ключ"""
    key_id: str
    zone_id: str
    
    # Key
    key_type: str = "KSK"  # KSK or ZSK
    algorithm: str = "RSASHA256"
    key_tag: int = 0
    
    # Status
    is_active: bool = True
    
    # Dates
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class DynamicDNSClient:
    """Клиент динамического DNS"""
    client_id: str
    zone_id: str
    
    # Client
    hostname: str = ""
    current_ip: str = ""
    
    # Auth
    username: str = ""
    password_hash: str = ""
    
    # Status
    is_active: bool = True
    last_update: Optional[datetime] = None


class DNSManager:
    """Менеджер DNS"""
    
    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.records: Dict[str, DNSRecord] = {}
        self.forwarders: Dict[str, Forwarder] = {}
        self.queries: List[DNSQuery] = []
        self.dnssec_keys: Dict[str, DNSSECKey] = {}
        self.ddns_clients: Dict[str, DynamicDNSClient] = {}
        
    async def create_zone(self, name: str,
                         zone_type: ZoneType = ZoneType.PRIMARY,
                         primary_ns: str = "",
                         admin_email: str = "") -> Zone:
        """Создание зоны"""
        zone = Zone(
            zone_id=f"zone_{uuid.uuid4().hex[:8]}",
            name=name,
            zone_type=zone_type,
            primary_ns=primary_ns or f"ns1.{name}",
            admin_email=admin_email or f"admin.{name}"
        )
        
        self.zones[zone.zone_id] = zone
        
        # Create default records
        if zone_type == ZoneType.PRIMARY:
            # SOA record (implicit)
            # NS records
            await self.create_record(zone.zone_id, "@", RecordType.NS, zone.primary_ns)
            
        return zone
        
    async def create_record(self, zone_id: str,
                           name: str,
                           record_type: RecordType,
                           value: str,
                           ttl: int = 3600,
                           priority: int = 0) -> Optional[DNSRecord]:
        """Создание записи"""
        zone = self.zones.get(zone_id)
        if not zone:
            return None
            
        record = DNSRecord(
            record_id=f"rec_{uuid.uuid4().hex[:8]}",
            zone_id=zone_id,
            name=name,
            record_type=record_type,
            value=value,
            ttl=ttl,
            priority=priority
        )
        
        self.records[record.record_id] = record
        zone.records.append(record.record_id)
        zone.serial += 1
        zone.updated_at = datetime.now()
        
        return record
        
    async def update_record(self, record_id: str,
                           value: str = None,
                           ttl: int = None,
                           priority: int = None) -> bool:
        """Обновление записи"""
        record = self.records.get(record_id)
        if not record:
            return False
            
        if value is not None:
            record.value = value
        if ttl is not None:
            record.ttl = ttl
        if priority is not None:
            record.priority = priority
            
        record.updated_at = datetime.now()
        
        zone = self.zones.get(record.zone_id)
        if zone:
            zone.serial += 1
            zone.updated_at = datetime.now()
            
        return True
        
    async def delete_record(self, record_id: str) -> bool:
        """Удаление записи"""
        record = self.records.get(record_id)
        if not record:
            return False
            
        zone = self.zones.get(record.zone_id)
        if zone and record_id in zone.records:
            zone.records.remove(record_id)
            zone.serial += 1
            zone.updated_at = datetime.now()
            
        del self.records[record_id]
        return True
        
    async def create_forwarder(self, name: str,
                              address: str,
                              port: int = 53,
                              domains: List[str] = None,
                              priority: int = 0) -> Forwarder:
        """Создание форвардера"""
        forwarder = Forwarder(
            forwarder_id=f"fwd_{uuid.uuid4().hex[:8]}",
            name=name,
            address=address,
            port=port,
            domains=domains or [],
            priority=priority
        )
        
        self.forwarders[forwarder.forwarder_id] = forwarder
        return forwarder
        
    async def enable_dnssec(self, zone_id: str) -> Optional[DNSSECKey]:
        """Включение DNSSEC"""
        zone = self.zones.get(zone_id)
        if not zone:
            return None
            
        # Create KSK
        ksk = DNSSECKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            zone_id=zone_id,
            key_type="KSK",
            algorithm="RSASHA256",
            key_tag=random.randint(10000, 65535)
        )
        
        self.dnssec_keys[ksk.key_id] = ksk
        
        # Create ZSK
        zsk = DNSSECKey(
            key_id=f"key_{uuid.uuid4().hex[:8]}",
            zone_id=zone_id,
            key_type="ZSK",
            algorithm="RSASHA256",
            key_tag=random.randint(10000, 65535)
        )
        
        self.dnssec_keys[zsk.key_id] = zsk
        
        zone.dnssec_status = DNSSECStatus.ENABLED
        
        return ksk
        
    async def create_ddns_client(self, zone_id: str,
                                hostname: str,
                                username: str,
                                password: str) -> Optional[DynamicDNSClient]:
        """Создание DDNS клиента"""
        zone = self.zones.get(zone_id)
        if not zone:
            return None
            
        client = DynamicDNSClient(
            client_id=f"ddns_{uuid.uuid4().hex[:8]}",
            zone_id=zone_id,
            hostname=hostname,
            username=username,
            password_hash=f"hash_{password}"
        )
        
        self.ddns_clients[client.client_id] = client
        return client
        
    async def update_ddns(self, client_id: str, ip_address: str) -> bool:
        """Обновление DDNS"""
        client = self.ddns_clients.get(client_id)
        if not client:
            return False
            
        zone = self.zones.get(client.zone_id)
        if not zone:
            return False
            
        # Find or create record
        record_found = None
        for record_id in zone.records:
            record = self.records.get(record_id)
            if record and record.name == client.hostname and record.record_type == RecordType.A:
                record_found = record
                break
                
        if record_found:
            await self.update_record(record_found.record_id, value=ip_address)
        else:
            await self.create_record(zone.zone_id, client.hostname, RecordType.A, ip_address, ttl=60)
            
        client.current_ip = ip_address
        client.last_update = datetime.now()
        
        return True
        
    async def query_dns(self, name: str,
                       query_type: RecordType,
                       client_ip: str = "127.0.0.1") -> List[DNSRecord]:
        """Выполнение DNS запроса"""
        # Find matching zone
        zone_match = None
        for zone in self.zones.values():
            if name.endswith(zone.name) or name == zone.name:
                zone_match = zone
                break
                
        results = []
        response_code = "NXDOMAIN"
        
        if zone_match:
            # Find matching records
            for record_id in zone_match.records:
                record = self.records.get(record_id)
                if not record or not record.is_active:
                    continue
                    
                record_name = record.name
                if record_name == "@":
                    record_name = zone_match.name
                elif not record_name.endswith(zone_match.name):
                    record_name = f"{record_name}.{zone_match.name}"
                    
                if record_name == name and record.record_type == query_type:
                    results.append(record)
                    record.query_count += 1
                    
            if results:
                response_code = "NOERROR"
            else:
                response_code = "NXDOMAIN"
                
        # Log query
        query = DNSQuery(
            query_id=f"qry_{uuid.uuid4().hex[:8]}",
            zone_id=zone_match.zone_id if zone_match else "",
            name=name,
            query_type=query_type,
            client_ip=client_ip,
            response_code=response_code,
            answer_count=len(results),
            response_time_ms=random.uniform(1, 50)
        )
        
        self.queries.append(query)
        
        if zone_match:
            zone_match.total_queries += 1
            
        return results
        
    def get_zone_records(self, zone_id: str) -> List[DNSRecord]:
        """Получение записей зоны"""
        zone = self.zones.get(zone_id)
        if not zone:
            return []
            
        return [self.records[rid] for rid in zone.records if rid in self.records]
        
    def export_zone(self, zone_id: str) -> str:
        """Экспорт зоны в BIND формат"""
        zone = self.zones.get(zone_id)
        if not zone:
            return ""
            
        lines = []
        lines.append(f"; Zone file for {zone.name}")
        lines.append(f"; Exported at {datetime.now().isoformat()}")
        lines.append("")
        lines.append(f"$ORIGIN {zone.name}.")
        lines.append(f"$TTL {zone.minimum_ttl}")
        lines.append("")
        
        # SOA record
        lines.append(f"@\tIN\tSOA\t{zone.primary_ns}. {zone.admin_email}. (")
        lines.append(f"\t\t\t{zone.serial}\t; serial")
        lines.append(f"\t\t\t{zone.refresh}\t; refresh")
        lines.append(f"\t\t\t{zone.retry}\t; retry")
        lines.append(f"\t\t\t{zone.expire}\t; expire")
        lines.append(f"\t\t\t{zone.minimum_ttl}\t; minimum")
        lines.append("\t\t\t)")
        lines.append("")
        
        # Other records
        for record_id in zone.records:
            record = self.records.get(record_id)
            if not record:
                continue
                
            if record.record_type == RecordType.MX:
                lines.append(f"{record.name}\t{record.ttl}\tIN\t{record.record_type.value}\t{record.priority}\t{record.value}")
            elif record.record_type == RecordType.SRV:
                lines.append(f"{record.name}\t{record.ttl}\tIN\t{record.record_type.value}\t{record.priority}\t{record.weight}\t{record.port}\t{record.value}")
            else:
                lines.append(f"{record.name}\t{record.ttl}\tIN\t{record.record_type.value}\t{record.value}")
                
        return "\n".join(lines)
        
    def get_query_analytics(self, zone_id: str = None,
                           hours: int = 24) -> Dict[str, Any]:
        """Аналитика запросов"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        queries = [
            q for q in self.queries
            if q.timestamp >= cutoff and (zone_id is None or q.zone_id == zone_id)
        ]
        
        by_type = {}
        by_response = {}
        by_hour = {}
        top_queried = {}
        
        total_response_time = 0
        
        for query in queries:
            # By type
            t = query.query_type.value
            by_type[t] = by_type.get(t, 0) + 1
            
            # By response
            r = query.response_code
            by_response[r] = by_response.get(r, 0) + 1
            
            # By hour
            hour = query.timestamp.strftime("%Y-%m-%d %H:00")
            by_hour[hour] = by_hour.get(hour, 0) + 1
            
            # Top queried
            top_queried[query.name] = top_queried.get(query.name, 0) + 1
            
            # Response time
            total_response_time += query.response_time_ms
            
        avg_response = total_response_time / len(queries) if queries else 0
        
        # Sort top queried
        top_10 = sorted(top_queried.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_queries": len(queries),
            "by_record_type": by_type,
            "by_response_code": by_response,
            "by_hour": by_hour,
            "top_queried": dict(top_10),
            "avg_response_time_ms": avg_response
        }
        
    def get_statistics(self) -> Dict[str, Any]:
        """Общая статистика"""
        total_zones = len(self.zones)
        active_zones = sum(1 for z in self.zones.values() if z.status == ZoneStatus.ACTIVE)
        
        by_zone_type = {}
        for z in self.zones.values():
            by_zone_type[z.zone_type.value] = by_zone_type.get(z.zone_type.value, 0) + 1
            
        total_records = len(self.records)
        
        by_record_type = {}
        for r in self.records.values():
            by_record_type[r.record_type.value] = by_record_type.get(r.record_type.value, 0) + 1
            
        dnssec_enabled = sum(1 for z in self.zones.values() 
                           if z.dnssec_status == DNSSECStatus.ENABLED)
                           
        total_queries = len(self.queries)
        total_forwarders = len(self.forwarders)
        active_forwarders = sum(1 for f in self.forwarders.values() if f.is_active)
        
        total_ddns = len(self.ddns_clients)
        active_ddns = sum(1 for c in self.ddns_clients.values() if c.is_active)
        
        return {
            "total_zones": total_zones,
            "active_zones": active_zones,
            "by_zone_type": by_zone_type,
            "total_records": total_records,
            "by_record_type": by_record_type,
            "dnssec_enabled": dnssec_enabled,
            "total_queries": total_queries,
            "total_forwarders": total_forwarders,
            "active_forwarders": active_forwarders,
            "total_ddns_clients": total_ddns,
            "active_ddns_clients": active_ddns
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 316: DNS Manager Platform")
    print("=" * 60)
    
    dns = DNSManager()
    print("✓ DNS Manager created")
    
    # Create zones
    print("\n🌐 Creating Zones...")
    
    zones_data = [
        ("example.com", ZoneType.PRIMARY, "ns1.example.com", "admin.example.com"),
        ("example.org", ZoneType.PRIMARY, "ns1.example.org", "admin.example.org"),
        ("internal.local", ZoneType.PRIMARY, "ns1.internal.local", "admin.internal.local"),
        ("10.in-addr.arpa", ZoneType.PRIMARY, "ns1.example.com", "admin.example.com")  # Reverse
    ]
    
    zones = []
    for name, z_type, ns, email in zones_data:
        zone = await dns.create_zone(name, z_type, ns, email)
        zones.append(zone)
        print(f"  🌐 {name} ({z_type.value})")
        
    # Create records
    print("\n📝 Creating DNS Records...")
    
    records_data = [
        (zones[0].zone_id, "@", RecordType.A, "192.168.1.1", 3600, 0),
        (zones[0].zone_id, "www", RecordType.A, "192.168.1.2", 3600, 0),
        (zones[0].zone_id, "mail", RecordType.A, "192.168.1.3", 3600, 0),
        (zones[0].zone_id, "@", RecordType.MX, "mail.example.com", 3600, 10),
        (zones[0].zone_id, "@", RecordType.MX, "mail2.example.com", 3600, 20),
        (zones[0].zone_id, "@", RecordType.TXT, "v=spf1 include:_spf.example.com ~all", 3600, 0),
        (zones[0].zone_id, "_dmarc", RecordType.TXT, "v=DMARC1; p=none;", 3600, 0),
        (zones[0].zone_id, "api", RecordType.CNAME, "www.example.com", 3600, 0),
        (zones[0].zone_id, "ns1", RecordType.A, "192.168.1.10", 3600, 0),
        (zones[0].zone_id, "ns2", RecordType.A, "192.168.1.11", 3600, 0),
        (zones[1].zone_id, "@", RecordType.A, "10.0.0.1", 3600, 0),
        (zones[1].zone_id, "www", RecordType.A, "10.0.0.2", 3600, 0),
        (zones[2].zone_id, "srv1", RecordType.A, "10.10.0.1", 300, 0),
        (zones[2].zone_id, "srv2", RecordType.A, "10.10.0.2", 300, 0),
        (zones[2].zone_id, "db", RecordType.A, "10.10.0.10", 300, 0)
    ]
    
    records = []
    for zone_id, name, r_type, value, ttl, priority in records_data:
        record = await dns.create_record(zone_id, name, r_type, value, ttl, priority)
        if record:
            records.append(record)
            
    print(f"  ✓ Created {len(records)} DNS records")
    
    # Create forwarders
    print("\n🔄 Creating Forwarders...")
    
    forwarders_data = [
        ("Google DNS", "8.8.8.8", 53, []),
        ("Google DNS 2", "8.8.4.4", 53, []),
        ("Cloudflare DNS", "1.1.1.1", 53, []),
        ("Internal DNS", "10.0.0.53", 53, ["internal.local"])
    ]
    
    for name, addr, port, domains in forwarders_data:
        fwd = await dns.create_forwarder(name, addr, port, domains)
        print(f"  🔄 {name} ({addr}:{port})")
        
    # Enable DNSSEC
    print("\n🔐 Enabling DNSSEC...")
    
    key = await dns.enable_dnssec(zones[0].zone_id)
    if key:
        print(f"  🔐 DNSSEC enabled for {zones[0].name}")
        print(f"     KSK Tag: {key.key_tag}")
        
    # Create DDNS clients
    print("\n🔄 Creating Dynamic DNS Clients...")
    
    ddns_data = [
        (zones[2].zone_id, "workstation1", "user1", "password1"),
        (zones[2].zone_id, "workstation2", "user2", "password2"),
        (zones[2].zone_id, "vpn-client", "vpn1", "vpnpass1")
    ]
    
    ddns_clients = []
    for zone_id, hostname, user, password in ddns_data:
        client = await dns.create_ddns_client(zone_id, hostname, user, password)
        if client:
            ddns_clients.append(client)
            print(f"  🔄 {hostname}.internal.local")
            
    # Update DDNS
    print("\n📡 Updating Dynamic DNS...")
    
    for i, client in enumerate(ddns_clients):
        ip = f"10.10.1.{100 + i}"
        await dns.update_ddns(client.client_id, ip)
        print(f"  📡 {client.hostname} -> {ip}")
        
    # Simulate queries
    print("\n🔍 Simulating DNS Queries...")
    
    query_data = [
        ("www.example.com", RecordType.A),
        ("mail.example.com", RecordType.A),
        ("example.com", RecordType.MX),
        ("api.example.com", RecordType.A),
        ("nonexistent.example.com", RecordType.A),
        ("www.example.org", RecordType.A),
        ("srv1.internal.local", RecordType.A),
        ("db.internal.local", RecordType.A)
    ]
    
    for _ in range(100):
        name, q_type = random.choice(query_data)
        client_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        await dns.query_dns(name, q_type, client_ip)
        
    print(f"  ✓ Processed {len(dns.queries)} queries")
    
    # Zone details
    print("\n🌐 Zone Details:")
    
    for zone in zones:
        zone_records = dns.get_zone_records(zone.zone_id)
        dnssec = "🔐" if zone.dnssec_status == DNSSECStatus.ENABLED else "⬜"
        
        print(f"\n  {dnssec} {zone.name}")
        print(f"     Type: {zone.zone_type.value}")
        print(f"     Status: {zone.status.value}")
        print(f"     Serial: {zone.serial}")
        print(f"     Records: {len(zone_records)}")
        print(f"     Queries: {zone.total_queries}")
        
    # Records table
    print("\n📝 DNS Records:")
    
    print("\n  ┌────────────────────────────┬────────┬──────────────────────────────────────┬───────┬──────────┐")
    print("  │ Name                       │ Type   │ Value                                │ TTL   │ Queries  │")
    print("  ├────────────────────────────┼────────┼──────────────────────────────────────┼───────┼──────────┤")
    
    for zone in zones[:2]:
        zone_records = dns.get_zone_records(zone.zone_id)
        for record in zone_records[:10]:
            full_name = record.name if record.name == "@" else f"{record.name}.{zone.name}"
            name = full_name[:26].ljust(26)
            r_type = record.record_type.value.ljust(6)
            value = record.value[:36].ljust(36)
            ttl = str(record.ttl).ljust(5)
            queries = str(record.query_count).ljust(8)
            
            print(f"  │ {name} │ {r_type} │ {value} │ {ttl} │ {queries} │")
            
    print("  └────────────────────────────┴────────┴──────────────────────────────────────┴───────┴──────────┘")
    
    # Query analytics
    print("\n📊 Query Analytics:")
    
    analytics = dns.get_query_analytics()
    
    print(f"\n  Total Queries: {analytics['total_queries']}")
    print(f"  Avg Response Time: {analytics['avg_response_time_ms']:.2f} ms")
    
    print("\n  By Record Type:")
    for r_type, count in analytics['by_record_type'].items():
        pct = count / analytics['total_queries'] * 100 if analytics['total_queries'] > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"    {r_type:10} [{bar}] {count} ({pct:.1f}%)")
        
    print("\n  By Response Code:")
    for code, count in analytics['by_response_code'].items():
        pct = count / analytics['total_queries'] * 100 if analytics['total_queries'] > 0 else 0
        print(f"    {code:15} {count} ({pct:.1f}%)")
        
    print("\n  Top Queried Names:")
    for name, count in list(analytics['top_queried'].items())[:5]:
        print(f"    {name:30} {count}")
        
    # Export zone
    print("\n📄 Zone Export (BIND format):")
    
    export = dns.export_zone(zones[0].zone_id)
    print("\n  " + "\n  ".join(export.split("\n")[:15]) + "\n  ...")
    
    # Statistics
    print("\n📊 DNS Statistics:")
    
    stats = dns.get_statistics()
    
    print(f"\n  Total Zones: {stats['total_zones']}")
    print(f"  Active Zones: {stats['active_zones']}")
    print("  By Zone Type:")
    for z_type, count in stats['by_zone_type'].items():
        print(f"    {z_type}: {count}")
        
    print(f"\n  Total Records: {stats['total_records']}")
    print("  By Record Type:")
    for r_type, count in sorted(stats['by_record_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {r_type}: {count}")
        
    print(f"\n  DNSSEC Enabled Zones: {stats['dnssec_enabled']}")
    print(f"  Total Queries: {stats['total_queries']}")
    
    print(f"\n  Forwarders: {stats['active_forwarders']}/{stats['total_forwarders']} active")
    print(f"  DDNS Clients: {stats['active_ddns_clients']}/{stats['total_ddns_clients']} active")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      DNS Manager Platform                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Zones:                 {stats['total_zones']:>12}                          │")
    print(f"│ Active Zones:                {stats['active_zones']:>12}                          │")
    print(f"│ Total Records:               {stats['total_records']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Queries:               {stats['total_queries']:>12}                          │")
    print(f"│ DNSSEC Enabled:              {stats['dnssec_enabled']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("DNS Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
