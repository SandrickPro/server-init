#!/usr/bin/env python3
"""
Server Init - Iteration 249: WebSocket Manager Platform
Платформа управления WebSocket соединениями

Функционал:
- Connection Management - управление соединениями
- Room Management - управление комнатами
- Message Broadcasting - рассылка сообщений
- Presence Tracking - отслеживание присутствия
- Heartbeat/Ping-Pong - проверка соединений
- Message Queue - очередь сообщений
- Connection Scaling - масштабирование
- Authentication - аутентификация соединений
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import uuid
import json


class ConnectionState(Enum):
    """Состояние соединения"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


class MessageType(Enum):
    """Тип сообщения"""
    TEXT = "text"
    BINARY = "binary"
    PING = "ping"
    PONG = "pong"
    CLOSE = "close"
    EVENT = "event"


class RoomType(Enum):
    """Тип комнаты"""
    PUBLIC = "public"
    PRIVATE = "private"
    DIRECT = "direct"
    BROADCAST = "broadcast"


class PresenceState(Enum):
    """Состояние присутствия"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class WebSocketConnection:
    """WebSocket соединение"""
    connection_id: str
    
    # Client info
    client_id: str = ""
    user_id: str = ""
    
    # State
    state: ConnectionState = ConnectionState.CONNECTING
    
    # Network
    remote_address: str = ""
    user_agent: str = ""
    
    # Protocol
    protocol: str = ""
    extensions: List[str] = field(default_factory=list)
    
    # Rooms
    rooms: Set[str] = field(default_factory=set)
    
    # Stats
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Heartbeat
    last_ping: datetime = field(default_factory=datetime.now)
    last_pong: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0
    
    # Time
    connected_at: datetime = field(default_factory=datetime.now)
    authenticated_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None


@dataclass
class Room:
    """Комната"""
    room_id: str
    name: str = ""
    
    # Type
    room_type: RoomType = RoomType.PUBLIC
    
    # Members
    members: Set[str] = field(default_factory=set)  # connection_ids
    max_members: int = 0  # 0 = unlimited
    
    # Options
    persistent: bool = False
    require_auth: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Stats
    message_count: int = 0
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Сообщение"""
    message_id: str
    
    # Type
    message_type: MessageType = MessageType.TEXT
    
    # Content
    event: str = ""
    data: Any = None
    
    # Routing
    from_connection: str = ""
    to_room: str = ""
    to_connection: str = ""
    broadcast: bool = False
    
    # Delivery
    delivered_to: Set[str] = field(default_factory=set)
    failed_for: Set[str] = field(default_factory=set)
    
    # Time
    created_at: datetime = field(default_factory=datetime.now)
    
    # Size
    size_bytes: int = 0


@dataclass
class PresenceInfo:
    """Информация о присутствии"""
    user_id: str
    
    # State
    state: PresenceState = PresenceState.ONLINE
    
    # Connections
    connections: Set[str] = field(default_factory=set)
    
    # Status
    status_message: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Time
    last_seen: datetime = field(default_factory=datetime.now)
    state_changed_at: datetime = field(default_factory=datetime.now)


@dataclass
class MessageQueue:
    """Очередь сообщений"""
    queue_id: str
    connection_id: str = ""
    
    # Messages
    messages: List[Message] = field(default_factory=list)
    max_size: int = 1000
    
    # Stats
    total_enqueued: int = 0
    total_delivered: int = 0
    total_dropped: int = 0


class WebSocketManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.rooms: Dict[str, Room] = {}
        self.presence: Dict[str, PresenceInfo] = {}
        self.message_queues: Dict[str, MessageQueue] = {}
        self.messages: List[Message] = []
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Heartbeat config
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_timeout = 60  # seconds
        
        # Stats
        self._total_connections = 0
        self._total_messages = 0
        
    async def connect(self, client_id: str, remote_address: str = "",
                     user_agent: str = "", protocol: str = "") -> WebSocketConnection:
        """Создание нового соединения"""
        conn = WebSocketConnection(
            connection_id=f"conn_{uuid.uuid4().hex[:8]}",
            client_id=client_id,
            remote_address=remote_address or f"192.168.1.{random.randint(1, 254)}",
            user_agent=user_agent,
            protocol=protocol
        )
        
        conn.state = ConnectionState.CONNECTED
        
        self.connections[conn.connection_id] = conn
        self._total_connections += 1
        
        # Create message queue
        queue = MessageQueue(
            queue_id=f"queue_{conn.connection_id}",
            connection_id=conn.connection_id
        )
        self.message_queues[conn.connection_id] = queue
        
        # Emit event
        await self._emit("connection", conn)
        
        return conn
        
    async def authenticate(self, connection_id: str, user_id: str,
                          metadata: Dict[str, Any] = None) -> bool:
        """Аутентификация соединения"""
        conn = self.connections.get(connection_id)
        if not conn:
            return False
            
        conn.user_id = user_id
        conn.state = ConnectionState.AUTHENTICATED
        conn.authenticated_at = datetime.now()
        
        # Update presence
        await self.set_presence(user_id, PresenceState.ONLINE)
        
        if user_id not in self.presence:
            self.presence[user_id] = PresenceInfo(user_id=user_id)
            
        self.presence[user_id].connections.add(connection_id)
        
        await self._emit("authenticated", conn)
        
        return True
        
    async def disconnect(self, connection_id: str, reason: str = ""):
        """Отключение соединения"""
        conn = self.connections.get(connection_id)
        if not conn:
            return
            
        conn.state = ConnectionState.DISCONNECTING
        
        # Leave all rooms
        for room_id in list(conn.rooms):
            await self.leave_room(connection_id, room_id)
            
        # Update presence
        if conn.user_id and conn.user_id in self.presence:
            presence = self.presence[conn.user_id]
            presence.connections.discard(connection_id)
            
            if not presence.connections:
                presence.state = PresenceState.OFFLINE
                presence.last_seen = datetime.now()
                
        conn.state = ConnectionState.DISCONNECTED
        conn.disconnected_at = datetime.now()
        
        # Clean up queue
        if connection_id in self.message_queues:
            del self.message_queues[connection_id]
            
        await self._emit("disconnection", conn, reason)
        
        del self.connections[connection_id]
        
    async def join_room(self, connection_id: str, room_id: str) -> bool:
        """Присоединение к комнате"""
        conn = self.connections.get(connection_id)
        if not conn:
            return False
            
        # Create room if not exists
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(
                room_id=room_id,
                name=room_id
            )
            
        room = self.rooms[room_id]
        
        # Check capacity
        if room.max_members > 0 and len(room.members) >= room.max_members:
            return False
            
        # Check auth
        if room.require_auth and conn.state != ConnectionState.AUTHENTICATED:
            return False
            
        room.members.add(connection_id)
        conn.rooms.add(room_id)
        room.last_activity = datetime.now()
        
        await self._emit("room_join", conn, room)
        
        return True
        
    async def leave_room(self, connection_id: str, room_id: str) -> bool:
        """Выход из комнаты"""
        conn = self.connections.get(connection_id)
        room = self.rooms.get(room_id)
        
        if not conn or not room:
            return False
            
        room.members.discard(connection_id)
        conn.rooms.discard(room_id)
        
        await self._emit("room_leave", conn, room)
        
        # Delete empty non-persistent rooms
        if not room.members and not room.persistent:
            del self.rooms[room_id]
            
        return True
        
    def create_room(self, name: str, room_type: RoomType = RoomType.PUBLIC,
                   max_members: int = 0, persistent: bool = False,
                   require_auth: bool = False) -> Room:
        """Создание комнаты"""
        room = Room(
            room_id=f"room_{uuid.uuid4().hex[:8]}",
            name=name,
            room_type=room_type,
            max_members=max_members,
            persistent=persistent,
            require_auth=require_auth
        )
        
        self.rooms[room.room_id] = room
        return room
        
    async def send_message(self, connection_id: str, event: str,
                          data: Any, message_type: MessageType = MessageType.EVENT):
        """Отправка сообщения в соединение"""
        conn = self.connections.get(connection_id)
        if not conn or conn.state == ConnectionState.DISCONNECTED:
            return
            
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            event=event,
            data=data,
            to_connection=connection_id,
            size_bytes=len(json.dumps(data, default=str))
        )
        
        # Simulate sending
        conn.messages_sent += 1
        conn.bytes_sent += message.size_bytes
        message.delivered_to.add(connection_id)
        
        self.messages.append(message)
        self._total_messages += 1
        
    async def broadcast_to_room(self, room_id: str, event: str,
                               data: Any, exclude: Set[str] = None):
        """Рассылка сообщения в комнату"""
        room = self.rooms.get(room_id)
        if not room:
            return
            
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=MessageType.EVENT,
            event=event,
            data=data,
            to_room=room_id,
            broadcast=True,
            size_bytes=len(json.dumps(data, default=str))
        )
        
        exclude = exclude or set()
        
        for conn_id in room.members:
            if conn_id in exclude:
                continue
                
            conn = self.connections.get(conn_id)
            if conn and conn.state != ConnectionState.DISCONNECTED:
                conn.messages_sent += 1
                conn.bytes_sent += message.size_bytes
                message.delivered_to.add(conn_id)
                
        room.message_count += 1
        room.last_activity = datetime.now()
        
        self.messages.append(message)
        self._total_messages += 1
        
    async def broadcast_all(self, event: str, data: Any):
        """Рассылка всем соединениям"""
        message = Message(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            message_type=MessageType.EVENT,
            event=event,
            data=data,
            broadcast=True,
            size_bytes=len(json.dumps(data, default=str))
        )
        
        for conn_id, conn in self.connections.items():
            if conn.state != ConnectionState.DISCONNECTED:
                conn.messages_sent += 1
                conn.bytes_sent += message.size_bytes
                message.delivered_to.add(conn_id)
                
        self.messages.append(message)
        self._total_messages += 1
        
    async def set_presence(self, user_id: str, state: PresenceState,
                          status_message: str = ""):
        """Установка статуса присутствия"""
        if user_id not in self.presence:
            self.presence[user_id] = PresenceInfo(user_id=user_id)
            
        presence = self.presence[user_id]
        old_state = presence.state
        
        presence.state = state
        presence.status_message = status_message
        presence.state_changed_at = datetime.now()
        
        if state != PresenceState.OFFLINE:
            presence.last_seen = datetime.now()
            
        # Notify about presence change
        if old_state != state:
            await self._emit("presence_change", user_id, old_state, state)
            
    async def ping(self, connection_id: str):
        """Отправка ping"""
        conn = self.connections.get(connection_id)
        if conn:
            conn.last_ping = datetime.now()
            
    async def pong(self, connection_id: str):
        """Получение pong"""
        conn = self.connections.get(connection_id)
        if conn:
            conn.last_pong = datetime.now()
            conn.latency_ms = (conn.last_pong - conn.last_ping).total_seconds() * 1000
            
    async def _emit(self, event: str, *args):
        """Эмит события"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                await handler(*args)
            except Exception:
                pass
                
    def on(self, event: str, handler: Callable):
        """Регистрация обработчика события"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    def get_room_members(self, room_id: str) -> List[WebSocketConnection]:
        """Получение членов комнаты"""
        room = self.rooms.get(room_id)
        if not room:
            return []
            
        return [
            self.connections[cid] for cid in room.members
            if cid in self.connections
        ]
        
    def get_user_connections(self, user_id: str) -> List[WebSocketConnection]:
        """Получение соединений пользователя"""
        return [
            conn for conn in self.connections.values()
            if conn.user_id == user_id
        ]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        active = sum(1 for c in self.connections.values() 
                    if c.state in [ConnectionState.CONNECTED, ConnectionState.AUTHENTICATED])
        authenticated = sum(1 for c in self.connections.values()
                          if c.state == ConnectionState.AUTHENTICATED)
                          
        online_users = sum(1 for p in self.presence.values() 
                         if p.state == PresenceState.ONLINE)
                         
        total_room_members = sum(len(r.members) for r in self.rooms.values())
        
        return {
            "total_connections": self._total_connections,
            "active_connections": active,
            "authenticated_connections": authenticated,
            "total_rooms": len(self.rooms),
            "total_room_members": total_room_members,
            "online_users": online_users,
            "total_messages": self._total_messages,
            "messages_stored": len(self.messages)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 249: WebSocket Manager Platform")
    print("=" * 60)
    
    manager = WebSocketManager()
    print("✓ WebSocket Manager created")
    
    # Create rooms
    print("\n🏠 Creating Rooms...")
    
    rooms_data = [
        ("general", RoomType.PUBLIC, 0, True),
        ("announcements", RoomType.BROADCAST, 0, True),
        ("vip-lounge", RoomType.PRIVATE, 50, True),
        ("support-chat", RoomType.PUBLIC, 100, False),
    ]
    
    rooms = []
    for name, rtype, max_members, persistent in rooms_data:
        room = manager.create_room(name, rtype, max_members, persistent)
        rooms.append(room)
        print(f"  🏠 {name} ({rtype.value})")
        
    # Simulate connections
    print("\n🔌 Simulating Connections...")
    
    connections = []
    users = ["alice", "bob", "carol", "dave", "eve"]
    
    for i, user in enumerate(users):
        conn = await manager.connect(
            f"client_{user}",
            f"192.168.1.{100 + i}",
            "Mozilla/5.0"
        )
        await manager.authenticate(conn.connection_id, user)
        connections.append(conn)
        print(f"  🔌 {user} connected (id: {conn.connection_id[:12]}...)")
        
    # Join rooms
    print("\n🚪 Joining Rooms...")
    
    for conn in connections[:4]:
        await manager.join_room(conn.connection_id, rooms[0].room_id)
        print(f"  ✓ {conn.user_id} joined {rooms[0].name}")
        
    for conn in connections[:2]:
        await manager.join_room(conn.connection_id, rooms[2].room_id)
        print(f"  ✓ {conn.user_id} joined {rooms[2].name}")
        
    # Send messages
    print("\n💬 Sending Messages...")
    
    # Direct message
    await manager.send_message(
        connections[0].connection_id,
        "notification",
        {"text": "Welcome to the chat!"}
    )
    print(f"  💬 Sent notification to {connections[0].user_id}")
    
    # Broadcast to room
    await manager.broadcast_to_room(
        rooms[0].room_id,
        "chat_message",
        {"user": "alice", "text": "Hello everyone!"},
        exclude={connections[0].connection_id}
    )
    print(f"  📢 Broadcast to {rooms[0].name}")
    
    # Broadcast to all
    await manager.broadcast_all(
        "announcement",
        {"text": "Server maintenance in 1 hour"}
    )
    print("  📣 Broadcast to all connections")
    
    # Update presence
    print("\n👤 Updating Presence...")
    
    await manager.set_presence(users[1], PresenceState.AWAY, "BRB")
    print(f"  👤 {users[1]} → away")
    
    await manager.set_presence(users[2], PresenceState.BUSY, "In a meeting")
    print(f"  👤 {users[2]} → busy")
    
    # Ping/Pong
    print("\n🏓 Heartbeat Check...")
    
    for conn in connections[:3]:
        await manager.ping(conn.connection_id)
        await asyncio.sleep(0.01)
        await manager.pong(conn.connection_id)
        print(f"  🏓 {conn.user_id}: {conn.latency_ms:.1f}ms")
        
    # Disconnect one user
    print("\n❌ Disconnecting User...")
    
    await manager.disconnect(connections[-1].connection_id, "user_logout")
    print(f"  ❌ {connections[-1].user_id} disconnected")
    
    # Display connections
    print("\n📊 Active Connections:")
    
    print("\n  ┌─────────────────┬──────────┬────────────────┬──────────┬──────────┐")
    print("  │ User            │ State    │ IP Address     │ Messages │ Rooms    │")
    print("  ├─────────────────┼──────────┼────────────────┼──────────┼──────────┤")
    
    for conn in manager.connections.values():
        user = conn.user_id[:15].ljust(15)
        state = conn.state.value[:8].ljust(8)
        ip = conn.remote_address[:14].ljust(14)
        msgs = str(conn.messages_sent)[:8].ljust(8)
        rooms_count = str(len(conn.rooms))[:8].ljust(8)
        
        print(f"  │ {user} │ {state} │ {ip} │ {msgs} │ {rooms_count} │")
        
    print("  └─────────────────┴──────────┴────────────────┴──────────┴──────────┘")
    
    # Display rooms
    print("\n🏠 Rooms:")
    
    print("\n  ┌─────────────────┬───────────┬──────────┬──────────┬──────────┐")
    print("  │ Room            │ Type      │ Members  │ Messages │ Status   │")
    print("  ├─────────────────┼───────────┼──────────┼──────────┼──────────┤")
    
    for room in manager.rooms.values():
        name = room.name[:15].ljust(15)
        rtype = room.room_type.value[:9].ljust(9)
        members = str(len(room.members))[:8].ljust(8)
        msgs = str(room.message_count)[:8].ljust(8)
        status = "🟢" if room.persistent else "🔵"
        
        print(f"  │ {name} │ {rtype} │ {members} │ {msgs} │ {status:8s} │")
        
    print("  └─────────────────┴───────────┴──────────┴──────────┴──────────┘")
    
    # Display presence
    print("\n👤 User Presence:")
    
    for user_id, presence in manager.presence.items():
        state_icon = {
            PresenceState.ONLINE: "🟢",
            PresenceState.AWAY: "🟡",
            PresenceState.BUSY: "🔴",
            PresenceState.OFFLINE: "⚫"
        }.get(presence.state, "⚪")
        
        status = f" - {presence.status_message}" if presence.status_message else ""
        conns = len(presence.connections)
        
        print(f"  {state_icon} {user_id}: {presence.state.value}{status} ({conns} connections)")
        
    # Room members
    print("\n👥 Room Members (general):")
    
    members = manager.get_room_members(rooms[0].room_id)
    for conn in members:
        print(f"  • {conn.user_id} ({conn.connection_id[:12]}...)")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Total Connections: {stats['total_connections']}")
    print(f"  Active Connections: {stats['active_connections']}")
    print(f"  Authenticated: {stats['authenticated_connections']}")
    
    print(f"\n  Total Rooms: {stats['total_rooms']}")
    print(f"  Total Room Members: {stats['total_room_members']}")
    print(f"  Online Users: {stats['online_users']}")
    
    print(f"\n  Total Messages: {stats['total_messages']}")
    
    # Connection state distribution
    print("\n📊 Connection States:")
    
    state_counts: Dict[ConnectionState, int] = {}
    for conn in manager.connections.values():
        state_counts[conn.state] = state_counts.get(conn.state, 0) + 1
        
    for state, count in state_counts.items():
        bar = "█" * count + "░" * (10 - count)
        print(f"  {state.value:15s} [{bar}] {count}")
        
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                   WebSocket Manager Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Connections:            {stats['active_connections']:>12}                        │")
    print(f"│ Authenticated:                 {stats['authenticated_connections']:>12}                        │")
    print(f"│ Total Rooms:                   {stats['total_rooms']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Online Users:                  {stats['online_users']:>12}                        │")
    print(f"│ Total Messages:                {stats['total_messages']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("WebSocket Manager Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
