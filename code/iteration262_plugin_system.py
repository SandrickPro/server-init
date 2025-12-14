#!/usr/bin/env python3
"""
Server Init - Iteration 262: Plugin System Platform
Платформа системы плагинов

Функционал:
- Plugin Discovery - обнаружение плагинов
- Plugin Loading - загрузка плагинов
- Plugin Lifecycle - жизненный цикл плагинов
- Extension Points - точки расширения
- Plugin Dependencies - зависимости плагинов
- Hot Reload - горячая перезагрузка
- Plugin Isolation - изоляция плагинов
- Plugin Marketplace - маркетплейс плагинов
"""

import asyncio
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import uuid


class PluginState(Enum):
    """Состояние плагина"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    UNLOADED = "unloaded"
    FAILED = "failed"


class PluginCategory(Enum):
    """Категория плагина"""
    CORE = "core"
    FEATURE = "feature"
    INTEGRATION = "integration"
    UI = "ui"
    ANALYTICS = "analytics"
    SECURITY = "security"


class ExtensionPointType(Enum):
    """Тип точки расширения"""
    HOOK = "hook"
    FILTER = "filter"
    ACTION = "action"
    PROVIDER = "provider"


@dataclass
class PluginMetadata:
    """Метаданные плагина"""
    plugin_id: str
    name: str
    version: str
    
    # Info
    author: str = ""
    description: str = ""
    
    # Category
    category: PluginCategory = PluginCategory.FEATURE
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # plugin_id
    optional_dependencies: List[str] = field(default_factory=list)
    
    # Compatibility
    min_version: str = "1.0.0"
    max_version: str = "99.0.0"
    
    # Extension points
    provides: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)


@dataclass
class ExtensionPoint:
    """Точка расширения"""
    point_id: str
    name: str
    
    # Type
    point_type: ExtensionPointType = ExtensionPointType.HOOK
    
    # Description
    description: str = ""
    
    # Handlers
    handlers: List[Callable] = field(default_factory=list)
    
    # Owner
    owner_plugin_id: Optional[str] = None


@dataclass
class Plugin:
    """Плагин"""
    plugin_id: str
    metadata: PluginMetadata
    
    # State
    state: PluginState = PluginState.DISCOVERED
    
    # Entry point
    entry_point: Optional[Callable] = None
    
    # Instance
    instance: Any = None
    
    # Provided extensions
    provided_extensions: Dict[str, List[Callable]] = field(default_factory=dict)
    
    # Timing
    loaded_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    
    # Error info
    error: Optional[str] = None


@dataclass
class PluginDependencyGraph:
    """Граф зависимостей плагинов"""
    # Plugin -> dependencies
    dependencies: Dict[str, Set[str]] = field(default_factory=dict)
    
    # Plugin -> dependents
    dependents: Dict[str, Set[str]] = field(default_factory=dict)


@dataclass
class PluginEvent:
    """Событие плагина"""
    event_id: str
    plugin_id: str
    
    # Event
    event_type: str = ""  # loaded, activated, deactivated, etc.
    
    # Details
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)


class PluginManager:
    """Менеджер плагинов"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.extension_points: Dict[str, ExtensionPoint] = {}
        self.dependency_graph = PluginDependencyGraph()
        self.events: List[PluginEvent] = []
        
    def register_extension_point(self, name: str,
                                point_type: ExtensionPointType = ExtensionPointType.HOOK,
                                description: str = "",
                                owner_plugin_id: str = None) -> ExtensionPoint:
        """Регистрация точки расширения"""
        point = ExtensionPoint(
            point_id=f"ext_{uuid.uuid4().hex[:8]}",
            name=name,
            point_type=point_type,
            description=description,
            owner_plugin_id=owner_plugin_id
        )
        
        self.extension_points[name] = point
        return point
        
    def discover_plugin(self, metadata: PluginMetadata) -> Plugin:
        """Обнаружение плагина"""
        plugin = Plugin(
            plugin_id=metadata.plugin_id,
            metadata=metadata,
            state=PluginState.DISCOVERED
        )
        
        self.plugins[plugin.plugin_id] = plugin
        
        # Update dependency graph
        self.dependency_graph.dependencies[plugin.plugin_id] = set(metadata.dependencies)
        for dep in metadata.dependencies:
            if dep not in self.dependency_graph.dependents:
                self.dependency_graph.dependents[dep] = set()
            self.dependency_graph.dependents[dep].add(plugin.plugin_id)
            
        self._emit_event(plugin.plugin_id, "discovered")
        
        return plugin
        
    def _emit_event(self, plugin_id: str, event_type: str, details: Dict[str, Any] = None):
        """Отправка события"""
        event = PluginEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            plugin_id=plugin_id,
            event_type=event_type,
            details=details or {}
        )
        self.events.append(event)
        
    def _check_dependencies(self, plugin_id: str) -> bool:
        """Проверка зависимостей"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False
            
        for dep_id in plugin.metadata.dependencies:
            dep = self.plugins.get(dep_id)
            if not dep or dep.state not in [PluginState.ACTIVATED, PluginState.INITIALIZED]:
                return False
                
        return True
        
    def _get_load_order(self) -> List[str]:
        """Получение порядка загрузки"""
        loaded = set()
        order = []
        
        def can_load(plugin_id: str) -> bool:
            deps = self.dependency_graph.dependencies.get(plugin_id, set())
            return all(d in loaded for d in deps)
            
        remaining = set(self.plugins.keys())
        
        while remaining:
            loaded_this_round = []
            
            for plugin_id in remaining:
                if can_load(plugin_id):
                    loaded_this_round.append(plugin_id)
                    
            if not loaded_this_round:
                # Circular dependency or missing dependency
                break
                
            for plugin_id in loaded_this_round:
                order.append(plugin_id)
                loaded.add(plugin_id)
                remaining.discard(plugin_id)
                
        return order
        
    async def load_plugin(self, plugin_id: str) -> bool:
        """Загрузка плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False
            
        if plugin.state != PluginState.DISCOVERED:
            return False
            
        # Check dependencies
        if not self._check_dependencies(plugin_id):
            plugin.state = PluginState.FAILED
            plugin.error = "Dependencies not met"
            return False
            
        try:
            # Simulate loading
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            plugin.state = PluginState.LOADED
            plugin.loaded_at = datetime.now()
            
            self._emit_event(plugin_id, "loaded")
            return True
            
        except Exception as e:
            plugin.state = PluginState.FAILED
            plugin.error = str(e)
            return False
            
    async def initialize_plugin(self, plugin_id: str) -> bool:
        """Инициализация плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin or plugin.state != PluginState.LOADED:
            return False
            
        try:
            # Simulate initialization
            await asyncio.sleep(random.uniform(0.01, 0.03))
            
            plugin.state = PluginState.INITIALIZED
            
            self._emit_event(plugin_id, "initialized")
            return True
            
        except Exception as e:
            plugin.state = PluginState.FAILED
            plugin.error = str(e)
            return False
            
    async def activate_plugin(self, plugin_id: str) -> bool:
        """Активация плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin or plugin.state != PluginState.INITIALIZED:
            return False
            
        try:
            # Register provided extensions
            for ext_name in plugin.metadata.provides:
                if ext_name in self.extension_points:
                    # Simulate extension handler
                    handler = lambda: f"Handler from {plugin_id}"
                    self.extension_points[ext_name].handlers.append(handler)
                    plugin.provided_extensions[ext_name] = [handler]
                    
            plugin.state = PluginState.ACTIVATED
            plugin.activated_at = datetime.now()
            
            self._emit_event(plugin_id, "activated")
            return True
            
        except Exception as e:
            plugin.state = PluginState.FAILED
            plugin.error = str(e)
            return False
            
    async def deactivate_plugin(self, plugin_id: str) -> bool:
        """Деактивация плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin or plugin.state != PluginState.ACTIVATED:
            return False
            
        # Check if other plugins depend on this one
        dependents = self.dependency_graph.dependents.get(plugin_id, set())
        active_dependents = [d for d in dependents 
                           if self.plugins.get(d) and self.plugins[d].state == PluginState.ACTIVATED]
        if active_dependents:
            return False  # Can't deactivate - other plugins depend on it
            
        try:
            # Remove provided extensions
            for ext_name, handlers in plugin.provided_extensions.items():
                if ext_name in self.extension_points:
                    for handler in handlers:
                        if handler in self.extension_points[ext_name].handlers:
                            self.extension_points[ext_name].handlers.remove(handler)
                            
            plugin.state = PluginState.DEACTIVATED
            plugin.provided_extensions.clear()
            
            self._emit_event(plugin_id, "deactivated")
            return True
            
        except Exception as e:
            plugin.error = str(e)
            return False
            
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Выгрузка плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False
            
        if plugin.state == PluginState.ACTIVATED:
            await self.deactivate_plugin(plugin_id)
            
        plugin.state = PluginState.UNLOADED
        plugin.instance = None
        
        self._emit_event(plugin_id, "unloaded")
        return True
        
    async def reload_plugin(self, plugin_id: str) -> bool:
        """Перезагрузка плагина"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False
            
        was_activated = plugin.state == PluginState.ACTIVATED
        
        # Unload
        await self.unload_plugin(plugin_id)
        
        # Reset state
        plugin.state = PluginState.DISCOVERED
        plugin.error = None
        
        # Reload
        if await self.load_plugin(plugin_id):
            if await self.initialize_plugin(plugin_id):
                if was_activated:
                    await self.activate_plugin(plugin_id)
                    
        self._emit_event(plugin_id, "reloaded")
        return plugin.state == PluginState.ACTIVATED
        
    async def load_all(self) -> Dict[str, bool]:
        """Загрузка всех плагинов"""
        results = {}
        load_order = self._get_load_order()
        
        for plugin_id in load_order:
            loaded = await self.load_plugin(plugin_id)
            if loaded:
                await self.initialize_plugin(plugin_id)
                await self.activate_plugin(plugin_id)
            results[plugin_id] = loaded
            
        return results
        
    def execute_extension_point(self, name: str, *args, **kwargs) -> List[Any]:
        """Выполнение точки расширения"""
        point = self.extension_points.get(name)
        if not point:
            return []
            
        results = []
        for handler in point.handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception:
                pass
                
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика плагинов"""
        states = {state: 0 for state in PluginState}
        categories = {cat: 0 for cat in PluginCategory}
        
        for plugin in self.plugins.values():
            states[plugin.state] += 1
            categories[plugin.metadata.category] += 1
            
        return {
            "plugins_total": len(self.plugins),
            "extension_points": len(self.extension_points),
            "events_total": len(self.events),
            "states": {s.value: c for s, c in states.items()},
            "categories": {c.value: ct for c, ct in categories.items()}
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 262: Plugin System Platform")
    print("=" * 60)
    
    manager = PluginManager()
    print("✓ Plugin Manager created")
    
    # Register extension points
    print("\n🔌 Registering Extension Points...")
    
    extension_points = [
        ("authentication", ExtensionPointType.PROVIDER, "Auth providers"),
        ("before_request", ExtensionPointType.HOOK, "Pre-request hooks"),
        ("after_response", ExtensionPointType.HOOK, "Post-response hooks"),
        ("data_transform", ExtensionPointType.FILTER, "Data transformers"),
        ("notification", ExtensionPointType.ACTION, "Notification handlers"),
    ]
    
    for name, ptype, desc in extension_points:
        point = manager.register_extension_point(name, ptype, desc)
        print(f"  🔌 {name}: {ptype.value}")
        
    # Discover plugins
    print("\n📦 Discovering Plugins...")
    
    plugins_data = [
        PluginMetadata(
            plugin_id="core-auth",
            name="Core Authentication",
            version="1.0.0",
            author="System",
            category=PluginCategory.CORE,
            provides=["authentication"]
        ),
        PluginMetadata(
            plugin_id="oauth-provider",
            name="OAuth Provider",
            version="2.0.0",
            author="Auth Team",
            category=PluginCategory.SECURITY,
            dependencies=["core-auth"],
            provides=["authentication"]
        ),
        PluginMetadata(
            plugin_id="analytics-tracker",
            name="Analytics Tracker",
            version="1.5.0",
            author="Analytics Team",
            category=PluginCategory.ANALYTICS,
            provides=["before_request", "after_response"]
        ),
        PluginMetadata(
            plugin_id="slack-integration",
            name="Slack Integration",
            version="1.2.0",
            author="Integrations Team",
            category=PluginCategory.INTEGRATION,
            dependencies=["core-auth"],
            provides=["notification"]
        ),
        PluginMetadata(
            plugin_id="data-encryption",
            name="Data Encryption",
            version="1.0.0",
            author="Security Team",
            category=PluginCategory.SECURITY,
            provides=["data_transform"]
        ),
    ]
    
    for metadata in plugins_data:
        plugin = manager.discover_plugin(metadata)
        deps = ", ".join(metadata.dependencies) if metadata.dependencies else "none"
        print(f"  📦 {metadata.name} v{metadata.version} (deps: {deps})")
        
    # Load all plugins
    print("\n🔄 Loading Plugins...")
    
    results = await manager.load_all()
    
    for plugin_id, success in results.items():
        plugin = manager.plugins[plugin_id]
        icon = "✅" if success else "❌"
        print(f"  {icon} {plugin.metadata.name}: {plugin.state.value}")
        
    # Display plugins
    print("\n📦 Plugin Status:")
    
    print("\n  ┌─────────────────────┬─────────────┬─────────────┬───────────────┬──────────┐")
    print("  │ Plugin              │ Version     │ Category    │ State         │ Provides │")
    print("  ├─────────────────────┼─────────────┼─────────────┼───────────────┼──────────┤")
    
    for plugin in manager.plugins.values():
        name = plugin.metadata.name[:19].ljust(19)
        version = plugin.metadata.version[:11].ljust(11)
        category = plugin.metadata.category.value[:11].ljust(11)
        state = plugin.state.value[:13].ljust(13)
        provides = str(len(plugin.metadata.provides))[:8].ljust(8)
        
        print(f"  │ {name} │ {version} │ {category} │ {state} │ {provides} │")
        
    print("  └─────────────────────┴─────────────┴─────────────┴───────────────┴──────────┘")
    
    # Extension points
    print("\n🔌 Extension Points:")
    
    print("\n  ┌─────────────────────┬───────────────┬──────────┬─────────────────────────────┐")
    print("  │ Extension Point     │ Type          │ Handlers │ Description                 │")
    print("  ├─────────────────────┼───────────────┼──────────┼─────────────────────────────┤")
    
    for point in manager.extension_points.values():
        name = point.name[:19].ljust(19)
        ptype = point.point_type.value[:13].ljust(13)
        handlers = str(len(point.handlers))[:8].ljust(8)
        desc = point.description[:27].ljust(27)
        
        print(f"  │ {name} │ {ptype} │ {handlers} │ {desc} │")
        
    print("  └─────────────────────┴───────────────┴──────────┴─────────────────────────────┘")
    
    # Dependency graph
    print("\n🔗 Dependency Graph:")
    
    for plugin_id, deps in manager.dependency_graph.dependencies.items():
        if deps:
            plugin = manager.plugins.get(plugin_id)
            deps_str = ", ".join(deps)
            print(f"  {plugin.metadata.name} -> [{deps_str}]")
            
    # Execute extension points
    print("\n⚡ Executing Extension Points:")
    
    for ext_name in ["authentication", "before_request", "notification"]:
        results = manager.execute_extension_point(ext_name)
        print(f"  {ext_name}: {len(results)} handlers executed")
        
    # Plugin lifecycle
    print("\n🔄 Plugin Lifecycle Test:")
    
    # Deactivate and reload a plugin
    test_plugin = "analytics-tracker"
    print(f"\n  Deactivating {test_plugin}...")
    await manager.deactivate_plugin(test_plugin)
    print(f"  State: {manager.plugins[test_plugin].state.value}")
    
    print(f"\n  Reloading {test_plugin}...")
    await manager.reload_plugin(test_plugin)
    print(f"  State: {manager.plugins[test_plugin].state.value}")
    
    # State distribution
    print("\n📊 State Distribution:")
    
    for state in PluginState:
        count = sum(1 for p in manager.plugins.values() if p.state == state)
        if count > 0:
            bar = "█" * count + "░" * (5 - count)
            print(f"  {state.value:13s} [{bar}] {count}")
            
    # Category distribution
    print("\n📊 Category Distribution:")
    
    for category in PluginCategory:
        count = sum(1 for p in manager.plugins.values() if p.metadata.category == category)
        if count > 0:
            bar = "█" * count + "░" * (5 - count)
            print(f"  {category.value:12s} [{bar}] {count}")
            
    # Recent events
    print("\n📜 Recent Events:")
    
    for event in manager.events[-8:]:
        plugin = manager.plugins.get(event.plugin_id)
        name = plugin.metadata.name if plugin else event.plugin_id
        print(f"  [{event.timestamp.strftime('%H:%M:%S')}] {name}: {event.event_type}")
        
    # Statistics
    print("\n📊 Manager Statistics:")
    
    stats = manager.get_statistics()
    
    print(f"\n  Plugins Total: {stats['plugins_total']}")
    print(f"  Extension Points: {stats['extension_points']}")
    print(f"  Events Total: {stats['events_total']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                      Plugin System Dashboard                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Plugins Total:                 {stats['plugins_total']:>12}                        │")
    print(f"│ Extension Points:              {stats['extension_points']:>12}                        │")
    print(f"│ Events Total:                  {stats['events_total']:>12}                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Activated:                     {stats['states']['activated']:>12}                        │")
    print(f"│ Failed:                        {stats['states']['failed']:>12}                        │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Plugin System Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
