#!/usr/bin/env python3
"""
Server Init - Iteration 309: Dashboard Builder Platform
Платформа построения дашбордов

Функционал:
- Dashboard Creation - создание дашбордов
- Widget Library - библиотека виджетов
- Data Sources - источники данных
- Real-time Updates - обновления в реальном времени
- Layout Management - управление разметкой
- Sharing & Permissions - шаринг и права
- Templates - шаблоны дашбордов
- Export - экспорт
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class WidgetType(Enum):
    """Тип виджета"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    GAUGE = "gauge"
    STAT = "stat"
    TABLE = "table"
    HEATMAP = "heatmap"
    TEXT = "text"
    ALERT_LIST = "alert_list"


class DataSourceType(Enum):
    """Тип источника данных"""
    PROMETHEUS = "prometheus"
    GRAPHITE = "graphite"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    API = "api"
    STATIC = "static"


class RefreshInterval(Enum):
    """Интервал обновления"""
    REAL_TIME = "5s"
    FAST = "10s"
    NORMAL = "30s"
    SLOW = "1m"
    VERY_SLOW = "5m"
    MANUAL = "manual"


class Permission(Enum):
    """Право доступа"""
    VIEW = "view"
    EDIT = "edit"
    ADMIN = "admin"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str
    source_type: DataSourceType
    
    # Connection
    connection_string: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Config
    default_query: str = ""
    timeout_seconds: int = 30
    
    # Status
    is_connected: bool = True
    last_check: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Query:
    """Запрос данных"""
    query_id: str
    name: str
    
    # Source
    source_id: str = ""
    
    # Query
    query_string: str = ""
    
    # Transform
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Cache
    cache_duration_seconds: int = 0


@dataclass
class Widget:
    """Виджет"""
    widget_id: str
    name: str
    widget_type: WidgetType
    
    # Position
    x: int = 0
    y: int = 0
    width: int = 6
    height: int = 4
    
    # Data
    query_ids: List[str] = field(default_factory=list)
    
    # Config
    config: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"title": "CPU Usage", "unit": "%", "thresholds": [...]}
    
    # Visualization
    colors: List[str] = field(default_factory=list)
    legend: bool = True
    
    # Refresh
    refresh_interval: RefreshInterval = RefreshInterval.NORMAL
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    name: str
    description: str
    
    # Layout
    widgets: List[str] = field(default_factory=list)  # widget_ids
    columns: int = 12
    
    # Time range
    time_range_start: str = "now-1h"
    time_range_end: str = "now"
    
    # Refresh
    refresh_interval: RefreshInterval = RefreshInterval.NORMAL
    
    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Organization
    folder: str = "General"
    tags: List[str] = field(default_factory=list)
    
    # Ownership
    owner_id: str = ""
    
    # Sharing
    is_public: bool = False
    shared_with: Dict[str, Permission] = field(default_factory=dict)
    
    # Favorites
    favorited_by: List[str] = field(default_factory=list)
    
    # Stats
    view_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardTemplate:
    """Шаблон дашборда"""
    template_id: str
    name: str
    description: str
    
    # Content
    dashboard_config: Dict[str, Any] = field(default_factory=dict)
    
    # Category
    category: str = "general"
    
    # Preview
    preview_image: str = ""
    
    # Usage
    usage_count: int = 0


@dataclass
class Annotation:
    """Аннотация"""
    annotation_id: str
    dashboard_id: str
    
    # Content
    title: str = ""
    text: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)
    end_timestamp: Optional[datetime] = None
    
    # Visual
    color: str = "#ff0000"


class DashboardBuilder:
    """Построитель дашбордов"""
    
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        self.queries: Dict[str, Query] = {}
        self.widgets: Dict[str, Widget] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.templates: Dict[str, DashboardTemplate] = {}
        self.annotations: Dict[str, Annotation] = {}
        
    async def add_data_source(self, name: str,
                             source_type: DataSourceType,
                             connection_string: str = "") -> DataSource:
        """Добавление источника данных"""
        source = DataSource(
            source_id=f"ds_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            connection_string=connection_string
        )
        
        self.data_sources[source.source_id] = source
        return source
        
    async def create_query(self, name: str,
                          source_id: str,
                          query_string: str) -> Optional[Query]:
        """Создание запроса"""
        source = self.data_sources.get(source_id)
        if not source:
            return None
            
        query = Query(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            name=name,
            source_id=source_id,
            query_string=query_string
        )
        
        self.queries[query.query_id] = query
        return query
        
    async def create_widget(self, name: str,
                           widget_type: WidgetType,
                           query_ids: List[str] = None,
                           config: Dict[str, Any] = None,
                           x: int = 0, y: int = 0,
                           width: int = 6, height: int = 4) -> Widget:
        """Создание виджета"""
        widget = Widget(
            widget_id=f"w_{uuid.uuid4().hex[:8]}",
            name=name,
            widget_type=widget_type,
            query_ids=query_ids or [],
            config=config or {},
            x=x, y=y,
            width=width, height=height
        )
        
        self.widgets[widget.widget_id] = widget
        return widget
        
    async def create_dashboard(self, name: str,
                              description: str = "",
                              owner_id: str = "",
                              folder: str = "General") -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            owner_id=owner_id,
            folder=folder
        )
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    async def add_widget_to_dashboard(self, dashboard_id: str,
                                     widget_id: str) -> bool:
        """Добавление виджета на дашборд"""
        dashboard = self.dashboards.get(dashboard_id)
        widget = self.widgets.get(widget_id)
        
        if not dashboard or not widget:
            return False
            
        if widget_id not in dashboard.widgets:
            dashboard.widgets.append(widget_id)
            dashboard.updated_at = datetime.now()
            
        return True
        
    async def update_widget_position(self, widget_id: str,
                                    x: int, y: int,
                                    width: int = None,
                                    height: int = None) -> bool:
        """Обновление позиции виджета"""
        widget = self.widgets.get(widget_id)
        if not widget:
            return False
            
        widget.x = x
        widget.y = y
        if width:
            widget.width = width
        if height:
            widget.height = height
            
        return True
        
    async def share_dashboard(self, dashboard_id: str,
                             user_id: str,
                             permission: Permission) -> bool:
        """Шаринг дашборда"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False
            
        dashboard.shared_with[user_id] = permission
        return True
        
    async def make_public(self, dashboard_id: str,
                         is_public: bool = True) -> bool:
        """Публикация дашборда"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False
            
        dashboard.is_public = is_public
        return True
        
    async def favorite_dashboard(self, dashboard_id: str,
                                user_id: str) -> bool:
        """Добавление в избранное"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False
            
        if user_id not in dashboard.favorited_by:
            dashboard.favorited_by.append(user_id)
            
        return True
        
    async def create_template(self, name: str,
                             description: str,
                             dashboard_id: str,
                             category: str = "general") -> Optional[DashboardTemplate]:
        """Создание шаблона из дашборда"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
            
        # Create config from dashboard
        config = {
            "name": dashboard.name,
            "widgets": [],
            "time_range": {
                "start": dashboard.time_range_start,
                "end": dashboard.time_range_end
            },
            "variables": dashboard.variables
        }
        
        for widget_id in dashboard.widgets:
            widget = self.widgets.get(widget_id)
            if widget:
                config["widgets"].append({
                    "type": widget.widget_type.value,
                    "name": widget.name,
                    "x": widget.x,
                    "y": widget.y,
                    "width": widget.width,
                    "height": widget.height,
                    "config": widget.config
                })
                
        template = DashboardTemplate(
            template_id=f"tpl_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            dashboard_config=config,
            category=category
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def create_from_template(self, template_id: str,
                                  name: str,
                                  owner_id: str) -> Optional[Dashboard]:
        """Создание дашборда из шаблона"""
        template = self.templates.get(template_id)
        if not template:
            return None
            
        dashboard = await self.create_dashboard(name, "", owner_id)
        
        config = template.dashboard_config
        dashboard.time_range_start = config.get("time_range", {}).get("start", "now-1h")
        dashboard.time_range_end = config.get("time_range", {}).get("end", "now")
        dashboard.variables = config.get("variables", {})
        
        # Create widgets
        for widget_config in config.get("widgets", []):
            widget = await self.create_widget(
                widget_config.get("name", "Widget"),
                WidgetType(widget_config.get("type", "stat")),
                config=widget_config.get("config", {}),
                x=widget_config.get("x", 0),
                y=widget_config.get("y", 0),
                width=widget_config.get("width", 6),
                height=widget_config.get("height", 4)
            )
            await self.add_widget_to_dashboard(dashboard.dashboard_id, widget.widget_id)
            
        template.usage_count += 1
        
        return dashboard
        
    async def add_annotation(self, dashboard_id: str,
                            title: str,
                            text: str = "",
                            tags: List[str] = None) -> Optional[Annotation]:
        """Добавление аннотации"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return None
            
        annotation = Annotation(
            annotation_id=f"ann_{uuid.uuid4().hex[:8]}",
            dashboard_id=dashboard_id,
            title=title,
            text=text,
            tags=tags or []
        )
        
        self.annotations[annotation.annotation_id] = annotation
        return annotation
        
    async def record_view(self, dashboard_id: str) -> bool:
        """Запись просмотра"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False
            
        dashboard.view_count += 1
        return True
        
    def get_dashboard_details(self, dashboard_id: str) -> Dict[str, Any]:
        """Получение деталей дашборда"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return {}
            
        widgets_details = []
        for widget_id in dashboard.widgets:
            widget = self.widgets.get(widget_id)
            if widget:
                widgets_details.append({
                    "widget_id": widget.widget_id,
                    "name": widget.name,
                    "type": widget.widget_type.value,
                    "position": {"x": widget.x, "y": widget.y},
                    "size": {"width": widget.width, "height": widget.height}
                })
                
        annotations = [
            a for a in self.annotations.values()
            if a.dashboard_id == dashboard_id
        ]
        
        return {
            "dashboard_id": dashboard_id,
            "name": dashboard.name,
            "description": dashboard.description,
            "folder": dashboard.folder,
            "tags": dashboard.tags,
            "owner_id": dashboard.owner_id,
            "widgets_count": len(dashboard.widgets),
            "widgets": widgets_details,
            "time_range": {
                "start": dashboard.time_range_start,
                "end": dashboard.time_range_end
            },
            "refresh_interval": dashboard.refresh_interval.value,
            "is_public": dashboard.is_public,
            "shared_with_count": len(dashboard.shared_with),
            "favorites_count": len(dashboard.favorited_by),
            "view_count": dashboard.view_count,
            "annotations_count": len(annotations),
            "created_at": dashboard.created_at.isoformat()
        }
        
    def search_dashboards(self, query: str = "",
                         folder: str = "",
                         tags: List[str] = None,
                         owner_id: str = "") -> List[Dashboard]:
        """Поиск дашбордов"""
        results = []
        
        for dashboard in self.dashboards.values():
            if folder and dashboard.folder != folder:
                continue
                
            if owner_id and dashboard.owner_id != owner_id:
                continue
                
            if tags:
                if not any(t in dashboard.tags for t in tags):
                    continue
                    
            if query:
                query_lower = query.lower()
                if (query_lower not in dashboard.name.lower() and
                    query_lower not in dashboard.description.lower()):
                    continue
                    
            results.append(dashboard)
            
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_folder = {}
        total_widgets = 0
        total_views = 0
        public_count = 0
        
        for dashboard in self.dashboards.values():
            by_folder[dashboard.folder] = by_folder.get(dashboard.folder, 0) + 1
            total_widgets += len(dashboard.widgets)
            total_views += dashboard.view_count
            if dashboard.is_public:
                public_count += 1
                
        widget_types = {}
        for widget in self.widgets.values():
            widget_types[widget.widget_type.value] = widget_types.get(widget.widget_type.value, 0) + 1
            
        source_types = {}
        for source in self.data_sources.values():
            source_types[source.source_type.value] = source_types.get(source.source_type.value, 0) + 1
            
        return {
            "total_dashboards": len(self.dashboards),
            "by_folder": by_folder,
            "public_dashboards": public_count,
            "total_widgets": len(self.widgets),
            "widgets_by_type": widget_types,
            "total_data_sources": len(self.data_sources),
            "sources_by_type": source_types,
            "total_queries": len(self.queries),
            "total_templates": len(self.templates),
            "total_annotations": len(self.annotations),
            "total_views": total_views,
            "avg_widgets_per_dashboard": total_widgets / max(len(self.dashboards), 1)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 309: Dashboard Builder Platform")
    print("=" * 60)
    
    builder = DashboardBuilder()
    print("✓ Dashboard Builder created")
    
    # Add data sources
    print("\n💾 Adding Data Sources...")
    
    sources_data = [
        ("Prometheus Metrics", DataSourceType.PROMETHEUS, "http://prometheus:9090"),
        ("InfluxDB Timeseries", DataSourceType.INFLUXDB, "http://influxdb:8086"),
        ("Elasticsearch Logs", DataSourceType.ELASTICSEARCH, "http://elasticsearch:9200"),
        ("PostgreSQL DB", DataSourceType.POSTGRESQL, "postgresql://localhost:5432/metrics")
    ]
    
    sources = []
    for name, s_type, conn in sources_data:
        source = await builder.add_data_source(name, s_type, conn)
        sources.append(source)
        print(f"  💾 {name} ({s_type.value})")
        
    # Create queries
    print("\n📊 Creating Queries...")
    
    queries_data = [
        ("CPU Usage", sources[0].source_id, 'rate(cpu_usage_seconds_total[5m])'),
        ("Memory Usage", sources[0].source_id, 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes'),
        ("Request Rate", sources[0].source_id, 'rate(http_requests_total[1m])'),
        ("Error Rate", sources[0].source_id, 'rate(http_requests_total{status=~"5.."}[1m])'),
        ("Response Time", sources[1].source_id, 'SELECT mean(response_time) FROM requests GROUP BY time(1m)'),
        ("Log Events", sources[2].source_id, '{"query": {"match_all": {}}}')
    ]
    
    queries = []
    for name, source_id, q_string in queries_data:
        query = await builder.create_query(name, source_id, q_string)
        queries.append(query)
        print(f"  📊 {name}")
        
    # Create widgets
    print("\n🔲 Creating Widgets...")
    
    widgets_data = [
        ("CPU Usage", WidgetType.GAUGE, [queries[0].query_id], 
         {"title": "CPU Usage", "unit": "%", "max": 100, "thresholds": [50, 80]}, 0, 0, 4, 4),
        ("Memory Usage", WidgetType.GAUGE, [queries[1].query_id],
         {"title": "Memory", "unit": "GB"}, 4, 0, 4, 4),
        ("Request Rate", WidgetType.STAT, [queries[2].query_id],
         {"title": "Requests/sec", "colorMode": "value"}, 8, 0, 4, 4),
        ("Traffic Over Time", WidgetType.LINE_CHART, [queries[2].query_id, queries[3].query_id],
         {"title": "Traffic", "legend": True}, 0, 4, 8, 6),
        ("Response Time Distribution", WidgetType.BAR_CHART, [queries[4].query_id],
         {"title": "Response Time", "unit": "ms"}, 8, 4, 4, 6),
        ("Error Rate", WidgetType.AREA_CHART, [queries[3].query_id],
         {"title": "Error Rate", "fill": 0.5}, 0, 10, 6, 4),
        ("Top Endpoints", WidgetType.TABLE, [],
         {"title": "Top Endpoints", "columns": ["endpoint", "requests", "avg_time"]}, 6, 10, 6, 4),
        ("System Health", WidgetType.HEATMAP, [],
         {"title": "Service Health Matrix"}, 0, 14, 12, 4)
    ]
    
    widgets = []
    for name, w_type, q_ids, config, x, y, w, h in widgets_data:
        widget = await builder.create_widget(name, w_type, q_ids, config, x, y, w, h)
        widgets.append(widget)
        print(f"  🔲 {name} ({w_type.value}) at ({x},{y}) size {w}x{h}")
        
    # Create dashboards
    print("\n📋 Creating Dashboards...")
    
    dashboards_data = [
        ("Infrastructure Overview", "Main infrastructure metrics", "user_001", "Infrastructure"),
        ("Application Performance", "App performance metrics", "user_001", "Applications"),
        ("Error Tracking", "Error monitoring dashboard", "user_002", "Monitoring"),
        ("Business Metrics", "Key business indicators", "user_003", "Business")
    ]
    
    dashboards = []
    for name, desc, owner, folder in dashboards_data:
        dashboard = await builder.create_dashboard(name, desc, owner, folder)
        dashboard.tags = ["production", folder.lower()]
        dashboards.append(dashboard)
        print(f"  📋 {name} ({folder})")
        
    # Add widgets to dashboards
    print("\n🔗 Adding Widgets to Dashboards...")
    
    # Infrastructure dashboard gets all widgets
    for widget in widgets:
        await builder.add_widget_to_dashboard(dashboards[0].dashboard_id, widget.widget_id)
        
    # App performance gets specific widgets
    for widget in widgets[:5]:
        await builder.add_widget_to_dashboard(dashboards[1].dashboard_id, widget.widget_id)
        
    # Error tracking
    for widget in [widgets[3], widgets[5]]:
        await builder.add_widget_to_dashboard(dashboards[2].dashboard_id, widget.widget_id)
        
    print(f"  ✓ Added widgets to {len(dashboards)} dashboards")
    
    # Share dashboards
    print("\n🔒 Setting Permissions...")
    
    await builder.share_dashboard(dashboards[0].dashboard_id, "user_002", Permission.VIEW)
    await builder.share_dashboard(dashboards[0].dashboard_id, "user_003", Permission.EDIT)
    await builder.make_public(dashboards[0].dashboard_id, True)
    
    print(f"  🔒 {dashboards[0].name}: public, shared with 2 users")
    
    await builder.share_dashboard(dashboards[1].dashboard_id, "user_002", Permission.VIEW)
    print(f"  🔒 {dashboards[1].name}: shared with 1 user")
    
    # Favorite dashboards
    print("\n⭐ Favoriting Dashboards...")
    
    await builder.favorite_dashboard(dashboards[0].dashboard_id, "user_001")
    await builder.favorite_dashboard(dashboards[0].dashboard_id, "user_002")
    await builder.favorite_dashboard(dashboards[0].dashboard_id, "user_003")
    await builder.favorite_dashboard(dashboards[1].dashboard_id, "user_001")
    
    print(f"  ⭐ {dashboards[0].name}: 3 favorites")
    print(f"  ⭐ {dashboards[1].name}: 1 favorite")
    
    # Record views
    print("\n👁️ Recording Views...")
    
    for _ in range(random.randint(50, 200)):
        await builder.record_view(dashboards[0].dashboard_id)
    for _ in range(random.randint(20, 100)):
        await builder.record_view(dashboards[1].dashboard_id)
    for _ in range(random.randint(10, 50)):
        await builder.record_view(dashboards[2].dashboard_id)
        
    print(f"  👁️ Recorded views for {len(dashboards)} dashboards")
    
    # Add annotations
    print("\n📝 Adding Annotations...")
    
    annotations_data = [
        (dashboards[0].dashboard_id, "Deployment v2.1.0", "Released new version", ["deploy"]),
        (dashboards[0].dashboard_id, "Incident INC-001", "Database failover", ["incident"]),
        (dashboards[1].dashboard_id, "Config Change", "Updated rate limits", ["config"])
    ]
    
    for dash_id, title, text, tags in annotations_data:
        await builder.add_annotation(dash_id, title, text, tags)
        print(f"  📝 {title}")
        
    # Create templates
    print("\n📑 Creating Templates...")
    
    template = await builder.create_template(
        "Infrastructure Template",
        "Standard infrastructure monitoring dashboard",
        dashboards[0].dashboard_id,
        "infrastructure"
    )
    print(f"  📑 {template.name}")
    
    # Create dashboard from template
    print("\n📋 Creating Dashboard from Template...")
    
    new_dash = await builder.create_from_template(
        template.template_id,
        "Staging Infrastructure",
        "user_002"
    )
    print(f"  📋 {new_dash.name} created from template")
    
    # Dashboard details
    print("\n📊 Dashboard Details:")
    
    for dashboard in dashboards[:3]:
        details = builder.get_dashboard_details(dashboard.dashboard_id)
        
        print(f"\n  📋 {details['name']}")
        print(f"     Folder: {details['folder']} | Widgets: {details['widgets_count']}")
        print(f"     Public: {'Yes' if details['is_public'] else 'No'} | Shared: {details['shared_with_count']}")
        print(f"     Views: {details['view_count']} | Favorites: {details['favorites_count']}")
        
        if details['widgets']:
            print(f"     Widgets:")
            for w in details['widgets'][:3]:
                print(f"       - {w['name']} ({w['type']})")
                
    # Search dashboards
    print("\n🔍 Search Results:")
    
    results = builder.search_dashboards(folder="Infrastructure")
    print(f"  Infrastructure folder: {len(results)} dashboards")
    
    results = builder.search_dashboards(query="performance")
    print(f"  Query 'performance': {len(results)} dashboards")
    
    results = builder.search_dashboards(tags=["production"])
    print(f"  Tag 'production': {len(results)} dashboards")
    
    # Dashboard list
    print("\n📋 Dashboard List:")
    
    print("\n  ┌────────────────────────────┬────────────────┬──────────┬────────┬────────┐")
    print("  │ Dashboard                  │ Folder         │ Widgets  │ Views  │ ⭐     │")
    print("  ├────────────────────────────┼────────────────┼──────────┼────────┼────────┤")
    
    for dashboard in builder.dashboards.values():
        name = dashboard.name[:26].ljust(26)
        folder = dashboard.folder[:14].ljust(14)
        widgets = str(len(dashboard.widgets)).ljust(8)
        views = str(dashboard.view_count).ljust(6)
        favs = str(len(dashboard.favorited_by)).ljust(6)
        
        print(f"  │ {name} │ {folder} │ {widgets} │ {views} │ {favs} │")
        
    print("  └────────────────────────────┴────────────────┴──────────┴────────┴────────┘")
    
    # Widget types distribution
    print("\n📊 Widget Types Distribution:")
    
    stats = builder.get_statistics()
    
    for w_type, count in stats['widgets_by_type'].items():
        bar = "█" * count + "░" * (8 - min(count, 8))
        print(f"  {w_type:15} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Builder Statistics:")
    
    print(f"\n  Total Dashboards: {stats['total_dashboards']}")
    print(f"  Public Dashboards: {stats['public_dashboards']}")
    
    print("\n  By Folder:")
    for folder, count in stats['by_folder'].items():
        print(f"    {folder}: {count}")
        
    print(f"\n  Total Widgets: {stats['total_widgets']}")
    print(f"  Avg Widgets/Dashboard: {stats['avg_widgets_per_dashboard']:.1f}")
    
    print(f"\n  Data Sources: {stats['total_data_sources']}")
    print(f"  Queries: {stats['total_queries']}")
    print(f"  Templates: {stats['total_templates']}")
    print(f"  Annotations: {stats['total_annotations']}")
    
    print(f"\n  Total Views: {stats['total_views']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Dashboard Builder Platform                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Dashboards:            {stats['total_dashboards']:>12}                          │")
    print(f"│ Total Widgets:               {stats['total_widgets']:>12}                          │")
    print(f"│ Total Data Sources:          {stats['total_data_sources']:>12}                          │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Views:                 {stats['total_views']:>12}                          │")
    print(f"│ Templates Available:         {stats['total_templates']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Dashboard Builder Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
