#!/usr/bin/env python3
"""
Server Init - Iteration 95: Dashboard Builder Platform
Платформа создания дашбордов

Функционал:
- Dashboard Creation - создание дашбордов
- Widget Library - библиотека виджетов
- Data Sources - источники данных
- Real-time Updates - обновления в реальном времени
- Layout Manager - управление разметкой
- Theming - темизация
- Export/Share - экспорт и шаринг
- Templates - шаблоны
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum
from collections import defaultdict
import uuid
import random


class WidgetType(Enum):
    """Тип виджета"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    STAT = "stat"
    TABLE = "table"
    TEXT = "text"
    HEATMAP = "heatmap"
    GRAPH = "graph"
    LOG = "log"
    ALERT_LIST = "alert_list"


class DataSourceType(Enum):
    """Тип источника данных"""
    PROMETHEUS = "prometheus"
    INFLUXDB = "influxdb"
    ELASTICSEARCH = "elasticsearch"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    STATIC = "static"
    API = "api"


class RefreshInterval(Enum):
    """Интервал обновления"""
    LIVE = 5
    FAST = 10
    NORMAL = 30
    SLOW = 60
    OFF = 0


class ThemeType(Enum):
    """Тип темы"""
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str = ""
    source_type: DataSourceType = DataSourceType.STATIC
    
    # Подключение
    url: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Настройки
    timeout_seconds: int = 30
    
    # Статус
    connected: bool = False
    last_query: Optional[datetime] = None


@dataclass
class Query:
    """Запрос данных"""
    query_id: str
    source_id: str = ""
    
    # Запрос
    expression: str = ""
    
    # Временной диапазон
    time_range: str = "1h"
    
    # Легенда
    legend: str = ""
    
    # Трансформации
    transformations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WidgetStyle:
    """Стиль виджета"""
    background_color: str = "#ffffff"
    border_color: str = "#e0e0e0"
    border_width: int = 1
    border_radius: int = 4
    padding: int = 16
    
    # Текст
    title_color: str = "#333333"
    title_size: int = 16
    
    # Цвета данных
    colors: List[str] = field(default_factory=lambda: [
        "#3366cc", "#dc3912", "#ff9900", "#109618", "#990099",
        "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395"
    ])


@dataclass
class Widget:
    """Виджет"""
    widget_id: str
    title: str = ""
    widget_type: WidgetType = WidgetType.STAT
    
    # Запросы
    queries: List[Query] = field(default_factory=list)
    
    # Позиция в сетке
    x: int = 0
    y: int = 0
    width: int = 6
    height: int = 4
    
    # Стиль
    style: WidgetStyle = field(default_factory=WidgetStyle)
    
    # Настройки виджета
    options: Dict[str, Any] = field(default_factory=dict)
    
    # Пороги для раскраски
    thresholds: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Row:
    """Строка дашборда"""
    row_id: str
    title: str = ""
    collapsed: bool = False
    height: int = 8
    
    # Виджеты
    widgets: List[Widget] = field(default_factory=list)


@dataclass 
class Variable:
    """Переменная дашборда"""
    var_id: str
    name: str = ""
    label: str = ""
    
    # Тип переменной
    var_type: str = "query"  # query, custom, constant, textbox
    
    # Значения
    query: str = ""
    options: List[str] = field(default_factory=list)
    current: str = ""
    
    # Настройки
    multi: bool = False
    include_all: bool = False


@dataclass
class Annotation:
    """Аннотация"""
    annotation_id: str
    name: str = ""
    
    # Источник
    source_id: str = ""
    query: str = ""
    
    # Стиль
    color: str = "#ff0000"
    enabled: bool = True


@dataclass
class Theme:
    """Тема"""
    theme_id: str
    name: str = ""
    theme_type: ThemeType = ThemeType.LIGHT
    
    # Цвета
    background: str = "#ffffff"
    panel_background: str = "#f5f5f5"
    text_primary: str = "#333333"
    text_secondary: str = "#666666"
    border: str = "#e0e0e0"
    
    # Акценты
    primary: str = "#3366cc"
    success: str = "#28a745"
    warning: str = "#ffc107"
    danger: str = "#dc3545"


@dataclass
class Dashboard:
    """Дашборд"""
    dashboard_id: str
    title: str = ""
    description: str = ""
    
    # Строки и виджеты
    rows: List[Row] = field(default_factory=list)
    
    # Переменные
    variables: List[Variable] = field(default_factory=list)
    
    # Аннотации
    annotations: List[Annotation] = field(default_factory=list)
    
    # Настройки
    refresh: RefreshInterval = RefreshInterval.NORMAL
    time_range: str = "1h"
    timezone: str = "UTC"
    
    # Тема
    theme: Optional[Theme] = None
    
    # Метаданные
    tags: List[str] = field(default_factory=list)
    folder: str = ""
    version: int = 1
    
    # Владелец
    owner: str = ""
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardTemplate:
    """Шаблон дашборда"""
    template_id: str
    name: str = ""
    description: str = ""
    
    # Категория
    category: str = ""
    
    # Содержимое
    dashboard_json: Dict[str, Any] = field(default_factory=dict)
    
    # Параметры для кастомизации
    parameters: List[Dict[str, str]] = field(default_factory=list)
    
    # Превью
    preview_image: str = ""


class DataSourceManager:
    """Менеджер источников данных"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        
    def add(self, name: str, source_type: DataSourceType,
             url: str = "", **kwargs) -> DataSource:
        """Добавление источника"""
        source = DataSource(
            source_id=f"ds_{uuid.uuid4().hex[:8]}",
            name=name,
            source_type=source_type,
            url=url,
            **kwargs
        )
        self.sources[source.source_id] = source
        return source
        
    async def test_connection(self, source_id: str) -> bool:
        """Тест подключения"""
        source = self.sources.get(source_id)
        if not source:
            return False
            
        # Симуляция теста
        await asyncio.sleep(0.1)
        source.connected = random.random() > 0.1
        return source.connected
        
    async def query(self, source_id: str, expression: str,
                     time_range: str = "1h") -> List[Dict[str, Any]]:
        """Выполнение запроса"""
        source = self.sources.get(source_id)
        if not source:
            return []
            
        source.last_query = datetime.now()
        
        # Симуляция данных
        await asyncio.sleep(0.05)
        
        data = []
        now = datetime.now()
        
        for i in range(60):
            timestamp = now - timedelta(minutes=60 - i)
            data.append({
                "timestamp": timestamp.isoformat(),
                "value": random.uniform(10, 100)
            })
            
        return data


class WidgetLibrary:
    """Библиотека виджетов"""
    
    def __init__(self):
        self.widget_templates: Dict[str, Dict[str, Any]] = {}
        self._setup_defaults()
        
    def _setup_defaults(self):
        """Настройка стандартных виджетов"""
        self.widget_templates = {
            "cpu_gauge": {
                "type": WidgetType.GAUGE,
                "title": "CPU Usage",
                "options": {
                    "min": 0,
                    "max": 100,
                    "unit": "%"
                },
                "thresholds": [
                    {"value": 0, "color": "#28a745"},
                    {"value": 70, "color": "#ffc107"},
                    {"value": 90, "color": "#dc3545"}
                ]
            },
            "memory_gauge": {
                "type": WidgetType.GAUGE,
                "title": "Memory Usage",
                "options": {
                    "min": 0,
                    "max": 100,
                    "unit": "%"
                }
            },
            "request_rate": {
                "type": WidgetType.LINE_CHART,
                "title": "Request Rate",
                "options": {
                    "unit": "req/s",
                    "legend": True,
                    "fill": True
                }
            },
            "error_rate": {
                "type": WidgetType.LINE_CHART,
                "title": "Error Rate",
                "options": {
                    "unit": "%",
                    "legend": True
                }
            },
            "uptime_stat": {
                "type": WidgetType.STAT,
                "title": "Uptime",
                "options": {
                    "format": "duration"
                }
            },
            "active_users": {
                "type": WidgetType.STAT,
                "title": "Active Users",
                "options": {
                    "format": "number"
                }
            }
        }
        
    def get_templates(self) -> List[Dict[str, Any]]:
        """Получение шаблонов"""
        return [
            {"id": k, **v} for k, v in self.widget_templates.items()
        ]
        
    def create_from_template(self, template_id: str, **overrides) -> Optional[Widget]:
        """Создание виджета из шаблона"""
        template = self.widget_templates.get(template_id)
        if not template:
            return None
            
        widget = Widget(
            widget_id=f"widget_{uuid.uuid4().hex[:8]}",
            title=overrides.get("title", template.get("title", "")),
            widget_type=template["type"],
            options=template.get("options", {}),
            thresholds=template.get("thresholds", [])
        )
        
        return widget


class LayoutManager:
    """Менеджер разметки"""
    
    GRID_COLUMNS = 24
    
    def auto_layout(self, widgets: List[Widget], columns: int = 2) -> List[Widget]:
        """Автоматическая раскладка"""
        widget_width = self.GRID_COLUMNS // columns
        
        for i, widget in enumerate(widgets):
            row = i // columns
            col = i % columns
            
            widget.x = col * widget_width
            widget.y = row * 8
            widget.width = widget_width
            widget.height = 8
            
        return widgets
        
    def fit_to_grid(self, widget: Widget) -> Widget:
        """Подгонка к сетке"""
        widget.x = max(0, min(widget.x, self.GRID_COLUMNS - widget.width))
        widget.width = max(1, min(widget.width, self.GRID_COLUMNS - widget.x))
        widget.y = max(0, widget.y)
        widget.height = max(1, widget.height)
        return widget


class ThemeManager:
    """Менеджер тем"""
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self._setup_defaults()
        
    def _setup_defaults(self):
        """Настройка стандартных тем"""
        # Light theme
        light = Theme(
            theme_id="theme_light",
            name="Light",
            theme_type=ThemeType.LIGHT,
            background="#ffffff",
            panel_background="#f5f5f5",
            text_primary="#333333",
            text_secondary="#666666",
            border="#e0e0e0"
        )
        self.themes[light.theme_id] = light
        
        # Dark theme
        dark = Theme(
            theme_id="theme_dark",
            name="Dark",
            theme_type=ThemeType.DARK,
            background="#1e1e1e",
            panel_background="#2d2d2d",
            text_primary="#ffffff",
            text_secondary="#b0b0b0",
            border="#404040"
        )
        self.themes[dark.theme_id] = dark
        
    def get(self, theme_id: str) -> Optional[Theme]:
        """Получение темы"""
        return self.themes.get(theme_id)
        
    def create_custom(self, name: str, **colors) -> Theme:
        """Создание кастомной темы"""
        theme = Theme(
            theme_id=f"theme_{uuid.uuid4().hex[:8]}",
            name=name,
            theme_type=ThemeType.CUSTOM,
            **colors
        )
        self.themes[theme.theme_id] = theme
        return theme


class TemplateManager:
    """Менеджер шаблонов"""
    
    def __init__(self):
        self.templates: Dict[str, DashboardTemplate] = {}
        self._setup_defaults()
        
    def _setup_defaults(self):
        """Настройка стандартных шаблонов"""
        # Infrastructure template
        infra = DashboardTemplate(
            template_id="template_infrastructure",
            name="Infrastructure Overview",
            description="Monitor servers, containers, and network",
            category="Infrastructure",
            parameters=[
                {"name": "host", "label": "Host", "default": "*"},
                {"name": "interval", "label": "Interval", "default": "1m"}
            ]
        )
        self.templates[infra.template_id] = infra
        
        # Application template
        app = DashboardTemplate(
            template_id="template_application",
            name="Application Performance",
            description="Monitor application metrics and errors",
            category="Application",
            parameters=[
                {"name": "service", "label": "Service", "default": "*"},
                {"name": "environment", "label": "Environment", "default": "production"}
            ]
        )
        self.templates[app.template_id] = app
        
        # Database template
        db = DashboardTemplate(
            template_id="template_database",
            name="Database Monitoring",
            description="Monitor database performance and queries",
            category="Database"
        )
        self.templates[db.template_id] = db
        
    def get_templates(self, category: str = None) -> List[DashboardTemplate]:
        """Получение шаблонов"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
            
        return templates


class DashboardExporter:
    """Экспортёр дашбордов"""
    
    def to_json(self, dashboard: Dashboard) -> str:
        """Экспорт в JSON"""
        data = {
            "id": dashboard.dashboard_id,
            "title": dashboard.title,
            "description": dashboard.description,
            "version": dashboard.version,
            "rows": [
                {
                    "id": row.row_id,
                    "title": row.title,
                    "collapsed": row.collapsed,
                    "widgets": [
                        {
                            "id": w.widget_id,
                            "title": w.title,
                            "type": w.widget_type.value,
                            "position": {"x": w.x, "y": w.y, "w": w.width, "h": w.height},
                            "options": w.options
                        }
                        for w in row.widgets
                    ]
                }
                for row in dashboard.rows
            ],
            "variables": [
                {"name": v.name, "current": v.current}
                for v in dashboard.variables
            ],
            "refresh": dashboard.refresh.value,
            "time_range": dashboard.time_range
        }
        
        return json.dumps(data, indent=2)
        
    def from_json(self, json_str: str) -> Dashboard:
        """Импорт из JSON"""
        data = json.loads(json_str)
        
        dashboard = Dashboard(
            dashboard_id=data.get("id", f"dash_{uuid.uuid4().hex[:8]}"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            version=data.get("version", 1)
        )
        
        # TODO: Parse rows, widgets, variables
        
        return dashboard


class DashboardBuilderPlatform:
    """Платформа создания дашбордов"""
    
    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.data_sources = DataSourceManager()
        self.widget_library = WidgetLibrary()
        self.layout_manager = LayoutManager()
        self.theme_manager = ThemeManager()
        self.template_manager = TemplateManager()
        self.exporter = DashboardExporter()
        
    def create_dashboard(self, title: str, description: str = "",
                          tags: List[str] = None, **kwargs) -> Dashboard:
        """Создание дашборда"""
        dashboard = Dashboard(
            dashboard_id=f"dash_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            tags=tags or [],
            **kwargs
        )
        self.dashboards[dashboard.dashboard_id] = dashboard
        return dashboard
        
    def create_from_template(self, template_id: str, title: str,
                              parameters: Dict[str, str] = None) -> Optional[Dashboard]:
        """Создание из шаблона"""
        template = self.template_manager.templates.get(template_id)
        if not template:
            return None
            
        dashboard = self.create_dashboard(
            title=title,
            description=template.description,
            tags=[template.category]
        )
        
        # Применяем параметры
        for param in template.parameters:
            var = Variable(
                var_id=f"var_{uuid.uuid4().hex[:8]}",
                name=param["name"],
                label=param.get("label", param["name"]),
                current=parameters.get(param["name"], param.get("default", ""))
            )
            dashboard.variables.append(var)
            
        return dashboard
        
    def add_row(self, dashboard_id: str, title: str = "",
                 collapsed: bool = False) -> Row:
        """Добавление строки"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        row = Row(
            row_id=f"row_{uuid.uuid4().hex[:8]}",
            title=title,
            collapsed=collapsed
        )
        dashboard.rows.append(row)
        return row
        
    def add_widget(self, dashboard_id: str, row_id: str,
                    widget_type: WidgetType, title: str,
                    **kwargs) -> Widget:
        """Добавление виджета"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        row = None
        for r in dashboard.rows:
            if r.row_id == row_id:
                row = r
                break
                
        if not row:
            raise ValueError(f"Row {row_id} not found")
            
        widget = Widget(
            widget_id=f"widget_{uuid.uuid4().hex[:8]}",
            title=title,
            widget_type=widget_type,
            **kwargs
        )
        
        # Auto-layout within row
        widget.y = 0
        widget.x = sum(w.width for w in row.widgets)
        
        row.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        
        return widget
        
    def add_query(self, dashboard_id: str, widget_id: str,
                   source_id: str, expression: str, **kwargs) -> Query:
        """Добавление запроса к виджету"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        # Находим виджет
        widget = None
        for row in dashboard.rows:
            for w in row.widgets:
                if w.widget_id == widget_id:
                    widget = w
                    break
                    
        if not widget:
            raise ValueError(f"Widget {widget_id} not found")
            
        query = Query(
            query_id=f"query_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            expression=expression,
            **kwargs
        )
        widget.queries.append(query)
        
        return query
        
    def add_variable(self, dashboard_id: str, name: str,
                      var_type: str = "query", **kwargs) -> Variable:
        """Добавление переменной"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        var = Variable(
            var_id=f"var_{uuid.uuid4().hex[:8]}",
            name=name,
            var_type=var_type,
            **kwargs
        )
        dashboard.variables.append(var)
        return var
        
    def export(self, dashboard_id: str) -> str:
        """Экспорт дашборда"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        return self.exporter.to_json(dashboard)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        total_widgets = sum(
            sum(len(row.widgets) for row in d.rows)
            for d in self.dashboards.values()
        )
        
        return {
            "dashboards": len(self.dashboards),
            "data_sources": len(self.data_sources.sources),
            "total_widgets": total_widgets,
            "templates": len(self.template_manager.templates),
            "themes": len(self.theme_manager.themes)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 95: Dashboard Builder Platform")
    print("=" * 60)
    
    async def demo():
        platform = DashboardBuilderPlatform()
        print("✓ Dashboard Builder Platform created")
        
        # Добавление источников данных
        print("\n📊 Adding Data Sources...")
        
        prometheus = platform.data_sources.add(
            "Prometheus",
            DataSourceType.PROMETHEUS,
            url="http://prometheus:9090"
        )
        
        influxdb = platform.data_sources.add(
            "InfluxDB",
            DataSourceType.INFLUXDB,
            url="http://influxdb:8086"
        )
        
        postgres = platform.data_sources.add(
            "PostgreSQL",
            DataSourceType.POSTGRESQL,
            url="postgresql://localhost:5432/metrics"
        )
        
        print(f"  ✓ {prometheus.name} ({prometheus.source_type.value})")
        print(f"  ✓ {influxdb.name} ({influxdb.source_type.value})")
        print(f"  ✓ {postgres.name} ({postgres.source_type.value})")
        
        # Тест подключения
        print("\n🔌 Testing Connections...")
        
        for source in platform.data_sources.sources.values():
            connected = await platform.data_sources.test_connection(source.source_id)
            status = "✅" if connected else "❌"
            print(f"  {status} {source.name}: {'connected' if connected else 'failed'}")
            
        # Шаблоны виджетов
        print("\n📦 Widget Templates:")
        
        for template in platform.widget_library.get_templates()[:4]:
            print(f"  • {template['id']}: {template['title']} ({template['type'].value})")
            
        # Шаблоны дашбордов
        print("\n📋 Dashboard Templates:")
        
        for template in platform.template_manager.get_templates():
            print(f"  • {template.name}")
            print(f"    {template.description}")
            
        # Создание дашборда
        print("\n🎨 Creating Dashboard...")
        
        dashboard = platform.create_dashboard(
            "Infrastructure Monitoring",
            description="Main infrastructure monitoring dashboard",
            tags=["infrastructure", "production"]
        )
        
        print(f"  ✓ Dashboard: {dashboard.title}")
        print(f"    ID: {dashboard.dashboard_id}")
        
        # Добавление переменных
        print("\n📝 Adding Variables...")
        
        platform.add_variable(
            dashboard.dashboard_id,
            "host",
            var_type="query",
            label="Host",
            query="label_values(node_cpu_seconds_total, instance)",
            options=["server-01", "server-02", "server-03"],
            current="server-01"
        )
        
        platform.add_variable(
            dashboard.dashboard_id,
            "interval",
            var_type="custom",
            label="Interval",
            options=["1m", "5m", "15m", "1h"],
            current="5m"
        )
        
        print(f"  ✓ Variables: {len(dashboard.variables)}")
        
        # Добавление строк и виджетов
        print("\n📊 Adding Rows and Widgets...")
        
        # Overview row
        overview_row = platform.add_row(dashboard.dashboard_id, "Overview")
        
        # CPU Gauge
        cpu_widget = platform.add_widget(
            dashboard.dashboard_id,
            overview_row.row_id,
            WidgetType.GAUGE,
            "CPU Usage",
            width=6,
            height=8,
            options={"min": 0, "max": 100, "unit": "%"},
            thresholds=[
                {"value": 0, "color": "#28a745"},
                {"value": 70, "color": "#ffc107"},
                {"value": 90, "color": "#dc3545"}
            ]
        )
        
        platform.add_query(
            dashboard.dashboard_id,
            cpu_widget.widget_id,
            prometheus.source_id,
            "100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
        )
        
        # Memory Gauge
        mem_widget = platform.add_widget(
            dashboard.dashboard_id,
            overview_row.row_id,
            WidgetType.GAUGE,
            "Memory Usage",
            width=6,
            height=8,
            options={"min": 0, "max": 100, "unit": "%"}
        )
        
        # Uptime Stat
        uptime_widget = platform.add_widget(
            dashboard.dashboard_id,
            overview_row.row_id,
            WidgetType.STAT,
            "Uptime",
            width=6,
            height=8,
            options={"format": "duration"}
        )
        
        # Active Connections
        conn_widget = platform.add_widget(
            dashboard.dashboard_id,
            overview_row.row_id,
            WidgetType.STAT,
            "Active Connections",
            width=6,
            height=8
        )
        
        print(f"  ✓ Row: {overview_row.title} ({len(overview_row.widgets)} widgets)")
        
        # Charts row
        charts_row = platform.add_row(dashboard.dashboard_id, "Performance Metrics")
        
        # Request Rate Chart
        requests_widget = platform.add_widget(
            dashboard.dashboard_id,
            charts_row.row_id,
            WidgetType.LINE_CHART,
            "Request Rate",
            width=12,
            height=10,
            options={"legend": True, "fill": True, "unit": "req/s"}
        )
        
        platform.add_query(
            dashboard.dashboard_id,
            requests_widget.widget_id,
            prometheus.source_id,
            "rate(http_requests_total[5m])"
        )
        
        # Response Time Chart
        latency_widget = platform.add_widget(
            dashboard.dashboard_id,
            charts_row.row_id,
            WidgetType.LINE_CHART,
            "Response Time",
            width=12,
            height=10,
            options={"legend": True, "unit": "ms"}
        )
        
        print(f"  ✓ Row: {charts_row.title} ({len(charts_row.widgets)} widgets)")
        
        # Table row
        table_row = platform.add_row(dashboard.dashboard_id, "Details", collapsed=True)
        
        # Top Endpoints Table
        endpoints_widget = platform.add_widget(
            dashboard.dashboard_id,
            table_row.row_id,
            WidgetType.TABLE,
            "Top Endpoints",
            width=24,
            height=12,
            options={
                "columns": ["endpoint", "requests", "avg_latency", "error_rate"]
            }
        )
        
        print(f"  ✓ Row: {table_row.title} ({len(table_row.widgets)} widgets, collapsed)")
        
        # Применение темы
        print("\n🎨 Applying Theme...")
        
        dark_theme = platform.theme_manager.get("theme_dark")
        dashboard.theme = dark_theme
        
        print(f"  ✓ Theme: {dark_theme.name}")
        print(f"    Background: {dark_theme.background}")
        print(f"    Text: {dark_theme.text_primary}")
        
        # Dashboard summary
        print("\n📋 Dashboard Summary:")
        
        print(f"\n  Title: {dashboard.title}")
        print(f"  Description: {dashboard.description}")
        print(f"  Tags: {', '.join(dashboard.tags)}")
        print(f"  Refresh: {dashboard.refresh.value}s")
        print(f"  Time Range: {dashboard.time_range}")
        
        print(f"\n  Rows: {len(dashboard.rows)}")
        
        total_widgets = 0
        for row in dashboard.rows:
            collapsed = " (collapsed)" if row.collapsed else ""
            print(f"    • {row.title}{collapsed}: {len(row.widgets)} widgets")
            total_widgets += len(row.widgets)
            
        print(f"\n  Total Widgets: {total_widgets}")
        print(f"  Variables: {len(dashboard.variables)}")
        
        # Widget preview
        print("\n  Widget Layout Preview (24-column grid):")
        print("  ┌────────────────────────────────────────────────────────────────┐")
        
        for row in dashboard.rows:
            if row.collapsed:
                print(f"  │ [▸ {row.title}]                                                 │")
            else:
                print(f"  │ {row.title}:                                                   │")
                for widget in row.widgets:
                    width_chars = widget.width * 2
                    box = "█" * min(width_chars, 20)
                    print(f"  │   [{box}] {widget.title[:15]:15}                      │")
                    
        print("  └────────────────────────────────────────────────────────────────┘")
        
        # Экспорт
        print("\n📤 Exporting Dashboard...")
        
        json_export = platform.export(dashboard.dashboard_id)
        print(f"  ✓ Exported {len(json_export)} bytes")
        
        # Показываем часть JSON
        export_preview = json.loads(json_export)
        print(f"\n  Preview:")
        print(f"    Title: {export_preview['title']}")
        print(f"    Rows: {len(export_preview['rows'])}")
        print(f"    Version: {export_preview['version']}")
        
        # Создание из шаблона
        print("\n📋 Creating Dashboard from Template...")
        
        template_dashboard = platform.create_from_template(
            "template_application",
            "API Service Monitoring",
            parameters={
                "service": "api-gateway",
                "environment": "production"
            }
        )
        
        if template_dashboard:
            print(f"  ✓ Created: {template_dashboard.title}")
            print(f"    Variables: {[v.name for v in template_dashboard.variables]}")
            
        # Статистика
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Dashboards: {stats['dashboards']}")
        print(f"  Data Sources: {stats['data_sources']}")
        print(f"  Total Widgets: {stats['total_widgets']}")
        print(f"  Templates: {stats['templates']}")
        print(f"  Themes: {stats['themes']}")
        
        # Dashboard
        print("\n📋 Dashboard Builder Overview:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Dashboard Builder Platform                     │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Dashboards:   {stats['dashboards']:>6}                                │")
        print(f"  │ Data Sources: {stats['data_sources']:>6}                                │")
        print(f"  │ Total Widgets:{stats['total_widgets']:>6}                                │")
        print(f"  │ Templates:    {stats['templates']:>6}                                │")
        print(f"  │ Themes:       {stats['themes']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Dashboard Builder Platform initialized!")
    print("=" * 60)
