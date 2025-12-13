#!/usr/bin/env python3
"""
Server Init - Iteration 96: Report Generator Platform
Платформа генерации отчётов

Функционал:
- Report Templates - шаблоны отчётов
- Data Aggregation - агрегация данных
- Scheduling - планирование
- Multiple Formats - форматы (PDF, HTML, Excel)
- Charts & Visualizations - графики
- Distribution - рассылка
- Report History - история отчётов
- Custom Reports - кастомные отчёты
"""

import json
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from enum import Enum
from collections import defaultdict
import uuid
import random


class ReportFormat(Enum):
    """Формат отчёта"""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"


class ReportPeriod(Enum):
    """Период отчёта"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class ChartType(Enum):
    """Тип графика"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    TABLE = "table"
    HEATMAP = "heatmap"


class ScheduleFrequency(Enum):
    """Частота расписания"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONCE = "once"


class ReportStatus(Enum):
    """Статус отчёта"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DataQuery:
    """Запрос данных"""
    query_id: str
    name: str = ""
    
    # Источник данных
    source: str = ""
    
    # Запрос
    query: str = ""
    
    # Параметры
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Трансформации
    aggregation: str = ""  # sum, avg, count, etc.
    group_by: List[str] = field(default_factory=list)
    order_by: str = ""


@dataclass
class ChartConfig:
    """Конфигурация графика"""
    chart_id: str
    title: str = ""
    chart_type: ChartType = ChartType.LINE
    
    # Данные
    data_query: Optional[DataQuery] = None
    
    # Оси
    x_axis: str = ""
    y_axis: str = ""
    
    # Стиль
    colors: List[str] = field(default_factory=list)
    legend: bool = True
    
    # Размер
    width: int = 600
    height: int = 400


@dataclass
class ReportSection:
    """Секция отчёта"""
    section_id: str
    title: str = ""
    
    # Содержимое
    content_type: str = "text"  # text, chart, table, metrics
    
    # Текст
    text: str = ""
    
    # Графики
    charts: List[ChartConfig] = field(default_factory=list)
    
    # Таблицы
    table_query: Optional[DataQuery] = None
    table_columns: List[str] = field(default_factory=list)
    
    # Метрики
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    
    # Порядок
    order: int = 0


@dataclass
class ReportTemplate:
    """Шаблон отчёта"""
    template_id: str
    name: str = ""
    description: str = ""
    
    # Секции
    sections: List[ReportSection] = field(default_factory=list)
    
    # Настройки
    period: ReportPeriod = ReportPeriod.DAILY
    formats: List[ReportFormat] = field(default_factory=lambda: [ReportFormat.PDF])
    
    # Стиль
    header: str = ""
    footer: str = ""
    logo: str = ""
    
    # Категория
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Schedule:
    """Расписание"""
    schedule_id: str
    template_id: str = ""
    
    # Частота
    frequency: ScheduleFrequency = ScheduleFrequency.DAILY
    
    # Время
    hour: int = 8
    minute: int = 0
    day_of_week: int = 0  # 0=Monday
    day_of_month: int = 1
    
    # Часовой пояс
    timezone: str = "UTC"
    
    # Статус
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # Рассылка
    recipients: List[str] = field(default_factory=list)


@dataclass
class GeneratedReport:
    """Сгенерированный отчёт"""
    report_id: str
    template_id: str = ""
    
    # Заголовок
    title: str = ""
    
    # Период данных
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Статус
    status: ReportStatus = ReportStatus.PENDING
    
    # Содержимое
    content: Dict[str, Any] = field(default_factory=dict)
    
    # Файлы
    files: Dict[ReportFormat, str] = field(default_factory=dict)
    
    # Метаданные
    generated_at: Optional[datetime] = None
    generation_time_seconds: float = 0
    
    # Ошибка
    error_message: str = ""


@dataclass
class Distribution:
    """Рассылка"""
    distribution_id: str
    report_id: str = ""
    
    # Получатели
    recipients: List[str] = field(default_factory=list)
    
    # Каналы
    channels: List[str] = field(default_factory=list)  # email, slack, teams
    
    # Статус
    sent: bool = False
    sent_at: Optional[datetime] = None
    
    # Результаты
    delivery_results: Dict[str, str] = field(default_factory=dict)


class DataAggregator:
    """Агрегатор данных"""
    
    async def execute_query(self, query: DataQuery,
                             period_start: datetime,
                             period_end: datetime) -> List[Dict[str, Any]]:
        """Выполнение запроса"""
        # Симуляция получения данных
        await asyncio.sleep(0.05)
        
        data = []
        current = period_start
        
        while current <= period_end:
            data.append({
                "timestamp": current.isoformat(),
                "value": random.uniform(10, 100),
                "count": random.randint(100, 1000)
            })
            current += timedelta(hours=1)
            
        return data
        
    def aggregate(self, data: List[Dict[str, Any]],
                   method: str, field: str) -> float:
        """Агрегация данных"""
        values = [d.get(field, 0) for d in data]
        
        if not values:
            return 0
            
        if method == "sum":
            return sum(values)
        elif method == "avg":
            return sum(values) / len(values)
        elif method == "min":
            return min(values)
        elif method == "max":
            return max(values)
        elif method == "count":
            return len(values)
        else:
            return sum(values)


class ChartRenderer:
    """Рендерер графиков"""
    
    def render(self, chart: ChartConfig,
                data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Рендеринг графика"""
        return {
            "chart_id": chart.chart_id,
            "title": chart.title,
            "type": chart.chart_type.value,
            "data": {
                "labels": [d.get(chart.x_axis, "") for d in data[:20]],
                "values": [d.get(chart.y_axis, d.get("value", 0)) for d in data[:20]]
            },
            "options": {
                "legend": chart.legend,
                "colors": chart.colors
            },
            "size": {
                "width": chart.width,
                "height": chart.height
            }
        }
        
    def render_ascii(self, chart: ChartConfig,
                      data: List[Dict[str, Any]], width: int = 50) -> str:
        """ASCII рендеринг для консоли"""
        values = [d.get("value", 0) for d in data[:10]]
        
        if not values:
            return "No data"
            
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        lines = [f"  {chart.title}"]
        lines.append("  " + "─" * width)
        
        if chart.chart_type == ChartType.BAR:
            for i, v in enumerate(values):
                bar_width = int((v - min_val) / range_val * (width - 10))
                bar = "█" * bar_width
                lines.append(f"  {i+1:2}│{bar} {v:.1f}")
        else:
            # Simple line representation
            for i, v in enumerate(values):
                pos = int((v - min_val) / range_val * (width - 5))
                line = " " * pos + "●"
                lines.append(f"  {i+1:2}│{line}")
                
        lines.append("  " + "─" * width)
        return "\n".join(lines)


class ReportRenderer:
    """Рендерер отчётов"""
    
    def __init__(self):
        self.chart_renderer = ChartRenderer()
        
    async def render_html(self, report: GeneratedReport,
                           template: ReportTemplate) -> str:
        """Рендеринг HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; }}
        .metric {{ display: inline-block; margin: 10px; padding: 20px; background: #f5f5f5; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <p>Period: {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}</p>
"""
        
        for section in template.sections:
            html += f"<h2>{section.title}</h2>\n"
            
            if section.content_type == "text":
                html += f"<p>{section.text}</p>\n"
                
            elif section.content_type == "metrics":
                for metric in section.metrics:
                    html += f"""
                    <div class="metric">
                        <div class="metric-value">{metric.get('value', 'N/A')}</div>
                        <div class="metric-label">{metric.get('label', '')}</div>
                    </div>
                    """
                    
            elif section.content_type == "table":
                data = report.content.get(f"section_{section.section_id}", [])
                if data:
                    html += "<table><tr>"
                    for col in section.table_columns:
                        html += f"<th>{col}</th>"
                    html += "</tr>"
                    
                    for row in data[:20]:
                        html += "<tr>"
                        for col in section.table_columns:
                            html += f"<td>{row.get(col, '')}</td>"
                        html += "</tr>"
                    html += "</table>"
                    
        html += f"""
    <footer>
        <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S') if report.generated_at else 'N/A'}</p>
    </footer>
</body>
</html>
"""
        return html
        
    async def render_markdown(self, report: GeneratedReport,
                               template: ReportTemplate) -> str:
        """Рендеринг Markdown"""
        md = f"# {report.title}\n\n"
        md += f"**Period:** {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}\n\n"
        
        for section in template.sections:
            md += f"## {section.title}\n\n"
            
            if section.content_type == "text":
                md += f"{section.text}\n\n"
                
            elif section.content_type == "metrics":
                for metric in section.metrics:
                    md += f"- **{metric.get('label', '')}**: {metric.get('value', 'N/A')}\n"
                md += "\n"
                
            elif section.content_type == "table":
                data = report.content.get(f"section_{section.section_id}", [])
                if data and section.table_columns:
                    # Header
                    md += "| " + " | ".join(section.table_columns) + " |\n"
                    md += "| " + " | ".join(["---"] * len(section.table_columns)) + " |\n"
                    
                    # Rows
                    for row in data[:20]:
                        values = [str(row.get(col, '')) for col in section.table_columns]
                        md += "| " + " | ".join(values) + " |\n"
                        
                md += "\n"
                
        md += f"\n---\n*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S') if report.generated_at else 'N/A'}*\n"
        return md


class DistributionManager:
    """Менеджер рассылки"""
    
    def __init__(self):
        self.distributions: List[Distribution] = []
        
    async def distribute(self, report: GeneratedReport,
                          recipients: List[str],
                          channels: List[str] = None) -> Distribution:
        """Рассылка отчёта"""
        channels = channels or ["email"]
        
        dist = Distribution(
            distribution_id=f"dist_{uuid.uuid4().hex[:8]}",
            report_id=report.report_id,
            recipients=recipients,
            channels=channels
        )
        
        # Симуляция отправки
        for recipient in recipients:
            for channel in channels:
                await asyncio.sleep(0.01)
                
                # Симуляция успеха/неуспеха
                if random.random() > 0.1:
                    dist.delivery_results[f"{recipient}:{channel}"] = "delivered"
                else:
                    dist.delivery_results[f"{recipient}:{channel}"] = "failed"
                    
        dist.sent = True
        dist.sent_at = datetime.now()
        
        self.distributions.append(dist)
        return dist


class ScheduleManager:
    """Менеджер расписаний"""
    
    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}
        
    def create(self, template_id: str, frequency: ScheduleFrequency,
                recipients: List[str], **kwargs) -> Schedule:
        """Создание расписания"""
        schedule = Schedule(
            schedule_id=f"sched_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            frequency=frequency,
            recipients=recipients,
            **kwargs
        )
        
        # Рассчитываем следующий запуск
        schedule.next_run = self._calculate_next_run(schedule)
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def _calculate_next_run(self, schedule: Schedule) -> datetime:
        """Расчёт следующего запуска"""
        now = datetime.now()
        
        if schedule.frequency == ScheduleFrequency.HOURLY:
            next_run = now.replace(minute=schedule.minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(hours=1)
                
        elif schedule.frequency == ScheduleFrequency.DAILY:
            next_run = now.replace(
                hour=schedule.hour,
                minute=schedule.minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
                
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            days_ahead = schedule.day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=schedule.hour,
                minute=schedule.minute,
                second=0,
                microsecond=0
            )
            
        else:
            next_run = now + timedelta(days=1)
            
        return next_run
        
    def get_due_schedules(self) -> List[Schedule]:
        """Получение готовых к выполнению расписаний"""
        now = datetime.now()
        return [
            s for s in self.schedules.values()
            if s.enabled and s.next_run and s.next_run <= now
        ]


class ReportGeneratorPlatform:
    """Платформа генерации отчётов"""
    
    def __init__(self):
        self.templates: Dict[str, ReportTemplate] = {}
        self.reports: Dict[str, GeneratedReport] = {}
        
        self.aggregator = DataAggregator()
        self.renderer = ReportRenderer()
        self.distribution_manager = DistributionManager()
        self.schedule_manager = ScheduleManager()
        
    def create_template(self, name: str, description: str = "",
                         period: ReportPeriod = ReportPeriod.DAILY,
                         **kwargs) -> ReportTemplate:
        """Создание шаблона"""
        template = ReportTemplate(
            template_id=f"tmpl_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            period=period,
            **kwargs
        )
        self.templates[template.template_id] = template
        return template
        
    def add_section(self, template_id: str, title: str,
                     content_type: str = "text", **kwargs) -> ReportSection:
        """Добавление секции"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        section = ReportSection(
            section_id=f"sec_{uuid.uuid4().hex[:8]}",
            title=title,
            content_type=content_type,
            order=len(template.sections),
            **kwargs
        )
        template.sections.append(section)
        template.updated_at = datetime.now()
        return section
        
    def add_chart(self, template_id: str, section_id: str,
                   title: str, chart_type: ChartType,
                   query: DataQuery = None, **kwargs) -> ChartConfig:
        """Добавление графика в секцию"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        section = None
        for s in template.sections:
            if s.section_id == section_id:
                section = s
                break
                
        if not section:
            raise ValueError(f"Section {section_id} not found")
            
        chart = ChartConfig(
            chart_id=f"chart_{uuid.uuid4().hex[:8]}",
            title=title,
            chart_type=chart_type,
            data_query=query,
            **kwargs
        )
        section.charts.append(chart)
        return chart
        
    async def generate(self, template_id: str,
                        period_start: datetime = None,
                        period_end: datetime = None,
                        formats: List[ReportFormat] = None) -> GeneratedReport:
        """Генерация отчёта"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
            
        # Определяем период
        period_end = period_end or datetime.now()
        
        if template.period == ReportPeriod.DAILY:
            period_start = period_start or (period_end - timedelta(days=1))
        elif template.period == ReportPeriod.WEEKLY:
            period_start = period_start or (period_end - timedelta(weeks=1))
        elif template.period == ReportPeriod.MONTHLY:
            period_start = period_start or (period_end - timedelta(days=30))
        else:
            period_start = period_start or (period_end - timedelta(days=1))
            
        # Создаём отчёт
        report = GeneratedReport(
            report_id=f"report_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            title=f"{template.name} - {period_end.strftime('%Y-%m-%d')}",
            period_start=period_start,
            period_end=period_end,
            status=ReportStatus.GENERATING
        )
        
        start_time = datetime.now()
        
        try:
            # Собираем данные для каждой секции
            for section in template.sections:
                if section.table_query:
                    data = await self.aggregator.execute_query(
                        section.table_query,
                        period_start,
                        period_end
                    )
                    report.content[f"section_{section.section_id}"] = data
                    
                for chart in section.charts:
                    if chart.data_query:
                        chart_data = await self.aggregator.execute_query(
                            chart.data_query,
                            period_start,
                            period_end
                        )
                        report.content[f"chart_{chart.chart_id}"] = chart_data
                        
            # Рендерим форматы
            formats = formats or template.formats
            
            if ReportFormat.HTML in formats:
                html = await self.renderer.render_html(report, template)
                report.files[ReportFormat.HTML] = html
                
            if ReportFormat.MARKDOWN in formats:
                md = await self.renderer.render_markdown(report, template)
                report.files[ReportFormat.MARKDOWN] = md
                
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.now()
            report.generation_time_seconds = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            
        self.reports[report.report_id] = report
        return report
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        completed = sum(1 for r in self.reports.values() if r.status == ReportStatus.COMPLETED)
        failed = sum(1 for r in self.reports.values() if r.status == ReportStatus.FAILED)
        
        return {
            "templates": len(self.templates),
            "generated_reports": len(self.reports),
            "completed": completed,
            "failed": failed,
            "schedules": len(self.schedule_manager.schedules),
            "distributions": len(self.distribution_manager.distributions)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 96: Report Generator Platform")
    print("=" * 60)
    
    async def demo():
        platform = ReportGeneratorPlatform()
        print("✓ Report Generator Platform created")
        
        # Создание шаблона
        print("\n📋 Creating Report Template...")
        
        template = platform.create_template(
            "Daily Operations Report",
            description="Daily summary of system operations and metrics",
            period=ReportPeriod.DAILY,
            formats=[ReportFormat.HTML, ReportFormat.MARKDOWN],
            category="Operations",
            tags=["daily", "operations", "metrics"]
        )
        
        print(f"  ✓ Template: {template.name}")
        print(f"    Period: {template.period.value}")
        print(f"    Formats: {[f.value for f in template.formats]}")
        
        # Добавление секций
        print("\n📝 Adding Sections...")
        
        # Executive Summary
        summary_section = platform.add_section(
            template.template_id,
            "Executive Summary",
            content_type="text",
            text="This report provides a comprehensive overview of system performance and operations for the reporting period."
        )
        print(f"  ✓ Section: {summary_section.title}")
        
        # Key Metrics
        metrics_section = platform.add_section(
            template.template_id,
            "Key Metrics",
            content_type="metrics",
            metrics=[
                {"label": "Total Requests", "value": "1,234,567"},
                {"label": "Success Rate", "value": "99.5%"},
                {"label": "Average Response Time", "value": "45ms"},
                {"label": "Active Users", "value": "5,432"}
            ]
        )
        print(f"  ✓ Section: {metrics_section.title}")
        
        # Performance Charts
        charts_section = platform.add_section(
            template.template_id,
            "Performance Charts",
            content_type="chart"
        )
        
        # Добавляем графики
        request_query = DataQuery(
            query_id=f"q_{uuid.uuid4().hex[:8]}",
            name="Request Rate",
            source="prometheus",
            query="rate(http_requests_total[5m])"
        )
        
        platform.add_chart(
            template.template_id,
            charts_section.section_id,
            "Request Rate",
            ChartType.LINE,
            query=request_query,
            x_axis="timestamp",
            y_axis="value"
        )
        
        platform.add_chart(
            template.template_id,
            charts_section.section_id,
            "Response Time Distribution",
            ChartType.BAR,
            x_axis="bucket",
            y_axis="count"
        )
        
        print(f"  ✓ Section: {charts_section.title} ({len(charts_section.charts)} charts)")
        
        # Top Endpoints Table
        table_section = platform.add_section(
            template.template_id,
            "Top Endpoints",
            content_type="table",
            table_query=DataQuery(
                query_id=f"q_{uuid.uuid4().hex[:8]}",
                name="Top Endpoints",
                source="logs",
                query="SELECT endpoint, count(*) as requests FROM logs GROUP BY endpoint ORDER BY requests DESC LIMIT 10"
            ),
            table_columns=["endpoint", "requests", "avg_latency", "error_rate"]
        )
        print(f"  ✓ Section: {table_section.title}")
        
        # Incidents
        incidents_section = platform.add_section(
            template.template_id,
            "Incidents & Alerts",
            content_type="text",
            text="No critical incidents were reported during this period. 3 warning alerts were triggered and resolved."
        )
        print(f"  ✓ Section: {incidents_section.title}")
        
        # Template summary
        print(f"\n  Total Sections: {len(template.sections)}")
        
        # Создание расписания
        print("\n⏰ Creating Schedule...")
        
        schedule = platform.schedule_manager.create(
            template.template_id,
            ScheduleFrequency.DAILY,
            recipients=["ops-team@company.com", "manager@company.com"],
            hour=8,
            minute=0
        )
        
        print(f"  ✓ Schedule: {schedule.frequency.value}")
        print(f"    Time: {schedule.hour:02d}:{schedule.minute:02d}")
        print(f"    Recipients: {schedule.recipients}")
        print(f"    Next Run: {schedule.next_run}")
        
        # Генерация отчёта
        print("\n🔄 Generating Report...")
        
        report = await platform.generate(
            template.template_id,
            period_start=datetime.now() - timedelta(days=1),
            period_end=datetime.now()
        )
        
        print(f"\n  Report ID: {report.report_id}")
        print(f"  Title: {report.title}")
        print(f"  Status: {report.status.value}")
        print(f"  Period: {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}")
        print(f"  Generation Time: {report.generation_time_seconds:.2f}s")
        
        # Доступные форматы
        print(f"\n  Generated Formats:")
        for fmt, content in report.files.items():
            size = len(content)
            print(f"    • {fmt.value}: {size} bytes")
            
        # Превью Markdown
        if ReportFormat.MARKDOWN in report.files:
            print("\n📄 Markdown Preview:")
            md_content = report.files[ReportFormat.MARKDOWN]
            # Показываем первые строки
            preview_lines = md_content.split('\n')[:15]
            for line in preview_lines:
                print(f"  {line}")
            if len(md_content.split('\n')) > 15:
                print("  ...")
                
        # Рассылка
        print("\n📤 Distributing Report...")
        
        distribution = await platform.distribution_manager.distribute(
            report,
            recipients=["ops-team@company.com", "manager@company.com"],
            channels=["email", "slack"]
        )
        
        print(f"  ✓ Distribution ID: {distribution.distribution_id}")
        print(f"    Recipients: {len(distribution.recipients)}")
        print(f"    Channels: {distribution.channels}")
        
        # Результаты доставки
        print("\n  Delivery Results:")
        delivered = sum(1 for r in distribution.delivery_results.values() if r == "delivered")
        failed = sum(1 for r in distribution.delivery_results.values() if r == "failed")
        print(f"    Delivered: {delivered}")
        print(f"    Failed: {failed}")
        
        # Генерируем ещё несколько отчётов для истории
        print("\n📊 Generating Additional Reports...")
        
        for i in range(3):
            r = await platform.generate(
                template.template_id,
                period_start=datetime.now() - timedelta(days=i+2),
                period_end=datetime.now() - timedelta(days=i+1)
            )
            
        print(f"  ✓ Generated 3 additional reports")
        
        # История отчётов
        print("\n📜 Report History:")
        
        for rid, r in list(platform.reports.items())[-5:]:
            status_icon = "✅" if r.status == ReportStatus.COMPLETED else "❌"
            print(f"  {status_icon} {r.title}")
            print(f"     Period: {r.period_start.strftime('%Y-%m-%d')}")
            print(f"     Generated: {r.generated_at.strftime('%H:%M:%S') if r.generated_at else 'N/A'}")
            
        # Chart preview (ASCII)
        print("\n📈 Chart Preview (ASCII):")
        
        chart_renderer = ChartRenderer()
        sample_data = [{"value": random.uniform(10, 100)} for _ in range(10)]
        
        chart = ChartConfig(
            chart_id="preview",
            title="Request Rate (sample)",
            chart_type=ChartType.BAR
        )
        
        ascii_chart = chart_renderer.render_ascii(chart, sample_data)
        print(ascii_chart)
        
        # Статистика
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Templates: {stats['templates']}")
        print(f"  Generated Reports: {stats['generated_reports']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Schedules: {stats['schedules']}")
        print(f"  Distributions: {stats['distributions']}")
        
        # Dashboard
        print("\n📋 Report Generator Dashboard:")
        print("  ┌─────────────────────────────────────────────────────────────┐")
        print("  │              Report Generator Overview                      │")
        print("  ├─────────────────────────────────────────────────────────────┤")
        print(f"  │ Templates:     {stats['templates']:>6}                                │")
        print(f"  │ Reports:       {stats['generated_reports']:>6}                                │")
        print(f"  │ Completed:     {stats['completed']:>6}                                │")
        print(f"  │ Schedules:     {stats['schedules']:>6}                                │")
        print(f"  │ Distributions: {stats['distributions']:>6}                                │")
        print("  └─────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Report Generator Platform initialized!")
    print("=" * 60)
