#!/usr/bin/env python3
"""
Server Init - Iteration 310: Report Generator Platform
Платформа генерации отчетов

Функционал:
- Report Templates - шаблоны отчетов
- Data Collection - сбор данных
- Scheduling - планирование отчетов
- Multiple Formats - множество форматов (PDF, Excel, HTML, CSV)
- Distribution - распространение отчетов
- Parameters - параметризация
- History - история отчетов
- Analytics - аналитика
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class ReportFormat(Enum):
    """Формат отчета"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"
    WORD = "word"


class ReportType(Enum):
    """Тип отчета"""
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    EXECUTIVE = "executive"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    CUSTOM = "custom"


class ReportStatus(Enum):
    """Статус отчета"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleFrequency(Enum):
    """Частота расписания"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class DeliveryMethod(Enum):
    """Метод доставки"""
    EMAIL = "email"
    SFTP = "sftp"
    S3 = "s3"
    WEBHOOK = "webhook"
    DOWNLOAD = "download"


@dataclass
class DataSource:
    """Источник данных"""
    source_id: str
    name: str
    
    # Connection
    connection_type: str = ""  # database, api, file
    connection_string: str = ""
    
    # Query
    default_query: str = ""
    
    # Status
    is_active: bool = True


@dataclass
class ReportParameter:
    """Параметр отчета"""
    param_id: str
    name: str
    param_type: str = "string"  # string, date, number, select
    
    # Default
    default_value: Any = None
    
    # Options
    options: List[str] = field(default_factory=list)
    
    # Validation
    required: bool = True


@dataclass
class ReportTemplate:
    """Шаблон отчета"""
    template_id: str
    name: str
    description: str
    report_type: ReportType
    
    # Data
    data_sources: List[str] = field(default_factory=list)
    
    # Parameters
    parameters: List[str] = field(default_factory=list)  # param_ids
    
    # Layout
    layout: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"sections": [...], "header": {...}, "footer": {...}}
    
    # Formats
    supported_formats: List[ReportFormat] = field(default_factory=list)
    default_format: ReportFormat = ReportFormat.PDF
    
    # Category
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    # Ownership
    owner_id: str = ""
    
    # Usage
    generation_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Report:
    """Сгенерированный отчет"""
    report_id: str
    template_id: str
    name: str
    
    # Generation
    status: ReportStatus = ReportStatus.PENDING
    format: ReportFormat = ReportFormat.PDF
    
    # Parameters
    parameters_values: Dict[str, Any] = field(default_factory=dict)
    
    # Time range
    time_range_start: Optional[datetime] = None
    time_range_end: Optional[datetime] = None
    
    # Output
    file_path: str = ""
    file_size_bytes: int = 0
    
    # Metadata
    generated_by: str = ""
    
    # Timing
    generation_started_at: Optional[datetime] = None
    generation_completed_at: Optional[datetime] = None
    generation_duration_seconds: float = 0
    
    # Error
    error_message: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Schedule:
    """Расписание отчета"""
    schedule_id: str
    template_id: str
    name: str
    
    # Frequency
    frequency: ScheduleFrequency = ScheduleFrequency.WEEKLY
    
    # Cron expression (for complex schedules)
    cron_expression: str = ""
    
    # Next run
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    
    # Parameters
    parameters_values: Dict[str, Any] = field(default_factory=dict)
    format: ReportFormat = ReportFormat.PDF
    
    # Delivery
    delivery_method: DeliveryMethod = DeliveryMethod.EMAIL
    delivery_config: Dict[str, Any] = field(default_factory=dict)
    # e.g., {"recipients": [...], "subject": "..."}
    
    # Status
    is_active: bool = True
    
    # Stats
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Delivery:
    """Доставка отчета"""
    delivery_id: str
    report_id: str
    
    # Method
    method: DeliveryMethod = DeliveryMethod.EMAIL
    destination: str = ""  # email, path, url
    
    # Status
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    
    # Error
    error_message: str = ""


class ReportGenerator:
    """Генератор отчетов"""
    
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        self.parameters: Dict[str, ReportParameter] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.reports: Dict[str, Report] = {}
        self.schedules: Dict[str, Schedule] = {}
        self.deliveries: Dict[str, Delivery] = {}
        
    async def add_data_source(self, name: str,
                             connection_type: str,
                             connection_string: str = "") -> DataSource:
        """Добавление источника данных"""
        source = DataSource(
            source_id=f"ds_{uuid.uuid4().hex[:8]}",
            name=name,
            connection_type=connection_type,
            connection_string=connection_string
        )
        
        self.data_sources[source.source_id] = source
        return source
        
    async def create_parameter(self, name: str,
                              param_type: str = "string",
                              default_value: Any = None,
                              options: List[str] = None,
                              required: bool = True) -> ReportParameter:
        """Создание параметра"""
        param = ReportParameter(
            param_id=f"param_{uuid.uuid4().hex[:8]}",
            name=name,
            param_type=param_type,
            default_value=default_value,
            options=options or [],
            required=required
        )
        
        self.parameters[param.param_id] = param
        return param
        
    async def create_template(self, name: str,
                             description: str,
                             report_type: ReportType,
                             owner_id: str = "",
                             category: str = "general") -> ReportTemplate:
        """Создание шаблона отчета"""
        template = ReportTemplate(
            template_id=f"tpl_{uuid.uuid4().hex[:8]}",
            name=name,
            description=description,
            report_type=report_type,
            owner_id=owner_id,
            category=category,
            supported_formats=[ReportFormat.PDF, ReportFormat.EXCEL, ReportFormat.CSV]
        )
        
        self.templates[template.template_id] = template
        return template
        
    async def add_data_source_to_template(self, template_id: str,
                                         source_id: str) -> bool:
        """Добавление источника данных в шаблон"""
        template = self.templates.get(template_id)
        source = self.data_sources.get(source_id)
        
        if not template or not source:
            return False
            
        if source_id not in template.data_sources:
            template.data_sources.append(source_id)
            template.updated_at = datetime.now()
            
        return True
        
    async def add_parameter_to_template(self, template_id: str,
                                       param_id: str) -> bool:
        """Добавление параметра в шаблон"""
        template = self.templates.get(template_id)
        param = self.parameters.get(param_id)
        
        if not template or not param:
            return False
            
        if param_id not in template.parameters:
            template.parameters.append(param_id)
            template.updated_at = datetime.now()
            
        return True
        
    async def generate_report(self, template_id: str,
                             name: str,
                             format: ReportFormat = ReportFormat.PDF,
                             parameters_values: Dict[str, Any] = None,
                             time_range_start: datetime = None,
                             time_range_end: datetime = None,
                             generated_by: str = "") -> Optional[Report]:
        """Генерация отчета"""
        template = self.templates.get(template_id)
        if not template:
            return None
            
        report = Report(
            report_id=f"rpt_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            name=name,
            format=format,
            parameters_values=parameters_values or {},
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            generated_by=generated_by
        )
        
        self.reports[report.report_id] = report
        
        # Simulate generation
        await self._process_report(report.report_id)
        
        template.generation_count += 1
        
        return report
        
    async def _process_report(self, report_id: str):
        """Обработка отчета (симуляция)"""
        report = self.reports.get(report_id)
        if not report:
            return
            
        report.status = ReportStatus.GENERATING
        report.generation_started_at = datetime.now()
        
        # Simulate generation time
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # 95% success rate
        if random.random() < 0.95:
            report.status = ReportStatus.COMPLETED
            report.file_path = f"/reports/{report.report_id}.{report.format.value}"
            report.file_size_bytes = random.randint(10000, 5000000)
        else:
            report.status = ReportStatus.FAILED
            report.error_message = "Generation failed: Data source timeout"
            
        report.generation_completed_at = datetime.now()
        report.generation_duration_seconds = (
            report.generation_completed_at - report.generation_started_at
        ).total_seconds()
        
    async def create_schedule(self, template_id: str,
                             name: str,
                             frequency: ScheduleFrequency,
                             delivery_method: DeliveryMethod,
                             delivery_config: Dict[str, Any] = None,
                             format: ReportFormat = ReportFormat.PDF) -> Optional[Schedule]:
        """Создание расписания"""
        template = self.templates.get(template_id)
        if not template:
            return None
            
        schedule = Schedule(
            schedule_id=f"sch_{uuid.uuid4().hex[:8]}",
            template_id=template_id,
            name=name,
            frequency=frequency,
            format=format,
            delivery_method=delivery_method,
            delivery_config=delivery_config or {}
        )
        
        # Calculate next run
        schedule.next_run = self._calculate_next_run(frequency)
        
        self.schedules[schedule.schedule_id] = schedule
        return schedule
        
    def _calculate_next_run(self, frequency: ScheduleFrequency) -> datetime:
        """Расчет следующего запуска"""
        now = datetime.now()
        
        if frequency == ScheduleFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ScheduleFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == ScheduleFrequency.MONTHLY:
            return now + timedelta(days=30)
        elif frequency == ScheduleFrequency.QUARTERLY:
            return now + timedelta(days=90)
        else:
            return now + timedelta(hours=1)
            
    async def run_schedule(self, schedule_id: str) -> Optional[Report]:
        """Запуск расписания"""
        schedule = self.schedules.get(schedule_id)
        if not schedule or not schedule.is_active:
            return None
            
        # Generate report
        report = await self.generate_report(
            schedule.template_id,
            f"{schedule.name} - {datetime.now().strftime('%Y-%m-%d')}",
            schedule.format,
            schedule.parameters_values,
            generated_by="scheduler"
        )
        
        if report:
            schedule.run_count += 1
            
            if report.status == ReportStatus.COMPLETED:
                schedule.success_count += 1
                
                # Deliver report
                await self.deliver_report(
                    report.report_id,
                    schedule.delivery_method,
                    schedule.delivery_config
                )
            else:
                schedule.failure_count += 1
                
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(schedule.frequency)
            
        return report
        
    async def deliver_report(self, report_id: str,
                            method: DeliveryMethod,
                            config: Dict[str, Any]) -> Optional[Delivery]:
        """Доставка отчета"""
        report = self.reports.get(report_id)
        if not report or report.status != ReportStatus.COMPLETED:
            return None
            
        destination = ""
        if method == DeliveryMethod.EMAIL:
            destination = ", ".join(config.get("recipients", []))
        elif method == DeliveryMethod.SFTP:
            destination = config.get("path", "")
        elif method == DeliveryMethod.S3:
            destination = config.get("bucket", "")
            
        delivery = Delivery(
            delivery_id=f"dlv_{uuid.uuid4().hex[:8]}",
            report_id=report_id,
            method=method,
            destination=destination
        )
        
        # Simulate delivery
        await asyncio.sleep(0.05)
        delivery.status = "sent"
        delivery.sent_at = datetime.now()
        
        self.deliveries[delivery.delivery_id] = delivery
        return delivery
        
    def get_template_reports(self, template_id: str,
                            limit: int = 10) -> List[Report]:
        """Получение отчетов шаблона"""
        reports = [
            r for r in self.reports.values()
            if r.template_id == template_id
        ]
        
        return sorted(reports, key=lambda r: r.created_at, reverse=True)[:limit]
        
    def get_report_history(self, days: int = 30) -> List[Report]:
        """Получение истории отчетов"""
        cutoff = datetime.now() - timedelta(days=days)
        
        reports = [
            r for r in self.reports.values()
            if r.created_at >= cutoff
        ]
        
        return sorted(reports, key=lambda r: r.created_at, reverse=True)
        
    def get_schedule_status(self, schedule_id: str) -> Dict[str, Any]:
        """Статус расписания"""
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return {}
            
        template = self.templates.get(schedule.template_id)
        
        success_rate = 0
        if schedule.run_count > 0:
            success_rate = schedule.success_count / schedule.run_count * 100
            
        return {
            "schedule_id": schedule_id,
            "name": schedule.name,
            "template": template.name if template else "Unknown",
            "frequency": schedule.frequency.value,
            "is_active": schedule.is_active,
            "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
            "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
            "run_count": schedule.run_count,
            "success_rate": success_rate,
            "delivery_method": schedule.delivery_method.value
        }
        
    def search_reports(self, query: str = "",
                      template_id: str = "",
                      status: ReportStatus = None,
                      format: ReportFormat = None) -> List[Report]:
        """Поиск отчетов"""
        results = []
        
        for report in self.reports.values():
            if template_id and report.template_id != template_id:
                continue
                
            if status and report.status != status:
                continue
                
            if format and report.format != format:
                continue
                
            if query:
                query_lower = query.lower()
                if query_lower not in report.name.lower():
                    continue
                    
            results.append(report)
            
        return results
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        by_status = {}
        by_format = {}
        total_size = 0
        total_duration = 0
        
        for report in self.reports.values():
            by_status[report.status.value] = by_status.get(report.status.value, 0) + 1
            by_format[report.format.value] = by_format.get(report.format.value, 0) + 1
            total_size += report.file_size_bytes
            total_duration += report.generation_duration_seconds
            
        by_type = {}
        for template in self.templates.values():
            by_type[template.report_type.value] = by_type.get(template.report_type.value, 0) + 1
            
        schedules_active = sum(1 for s in self.schedules.values() if s.is_active)
        
        return {
            "total_templates": len(self.templates),
            "by_type": by_type,
            "total_reports": len(self.reports),
            "by_status": by_status,
            "by_format": by_format,
            "total_schedules": len(self.schedules),
            "active_schedules": schedules_active,
            "total_deliveries": len(self.deliveries),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "avg_generation_time": total_duration / max(len(self.reports), 1)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 310: Report Generator Platform")
    print("=" * 60)
    
    generator = ReportGenerator()
    print("✓ Report Generator created")
    
    # Add data sources
    print("\n💾 Adding Data Sources...")
    
    sources_data = [
        ("Metrics Database", "database", "postgresql://metrics:5432/metrics"),
        ("Business Data", "database", "mysql://business:3306/analytics"),
        ("External API", "api", "https://api.example.com/data"),
        ("CSV Files", "file", "/data/reports/")
    ]
    
    sources = []
    for name, conn_type, conn_str in sources_data:
        source = await generator.add_data_source(name, conn_type, conn_str)
        sources.append(source)
        print(f"  💾 {name} ({conn_type})")
        
    # Create parameters
    print("\n⚙️ Creating Parameters...")
    
    params_data = [
        ("date_from", "date", None, [], True),
        ("date_to", "date", None, [], True),
        ("region", "select", "all", ["all", "us", "eu", "asia"], True),
        ("department", "select", "all", ["all", "sales", "engineering", "marketing"], False),
        ("format_style", "select", "detailed", ["summary", "detailed"], False)
    ]
    
    params = []
    for name, p_type, default, options, required in params_data:
        param = await generator.create_parameter(name, p_type, default, options, required)
        params.append(param)
        print(f"  ⚙️ {name} ({p_type})")
        
    # Create templates
    print("\n📝 Creating Templates...")
    
    templates_data = [
        ("Daily Operations Report", "Operational metrics and KPIs", ReportType.OPERATIONAL, "operations"),
        ("Weekly Analytics Summary", "Business analytics overview", ReportType.ANALYTICAL, "analytics"),
        ("Executive Dashboard", "Executive summary for leadership", ReportType.EXECUTIVE, "executive"),
        ("Compliance Report", "Regulatory compliance status", ReportType.COMPLIANCE, "compliance"),
        ("Audit Trail Report", "Security audit trail", ReportType.AUDIT, "security"),
        ("Custom Sales Report", "Customizable sales metrics", ReportType.CUSTOM, "sales")
    ]
    
    templates = []
    for name, desc, r_type, category in templates_data:
        template = await generator.create_template(name, desc, r_type, "user_001", category)
        template.tags = [category, r_type.value]
        templates.append(template)
        
        # Add data sources
        for source in sources[:2]:
            await generator.add_data_source_to_template(template.template_id, source.source_id)
            
        # Add parameters
        for param in params[:3]:
            await generator.add_parameter_to_template(template.template_id, param.param_id)
            
        print(f"  📝 {name} ({r_type.value})")
        
    # Generate reports
    print("\n📊 Generating Reports...")
    
    generated_reports = []
    for i in range(20):
        template = random.choice(templates)
        format = random.choice([ReportFormat.PDF, ReportFormat.EXCEL, ReportFormat.CSV])
        
        report = await generator.generate_report(
            template.template_id,
            f"{template.name} - {datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{i}",
            format,
            {"region": random.choice(["all", "us", "eu"]), "date_from": "2024-01-01"},
            datetime.now() - timedelta(days=7),
            datetime.now(),
            f"user_{random.randint(1, 5):03d}"
        )
        
        if report:
            generated_reports.append(report)
            
    completed = sum(1 for r in generated_reports if r.status == ReportStatus.COMPLETED)
    print(f"  ✓ Generated {len(generated_reports)} reports ({completed} completed)")
    
    # Create schedules
    print("\n📅 Creating Schedules...")
    
    schedules_data = [
        ("Daily Ops Report", templates[0].template_id, ScheduleFrequency.DAILY, 
         DeliveryMethod.EMAIL, {"recipients": ["ops@example.com", "manager@example.com"]}),
        ("Weekly Analytics", templates[1].template_id, ScheduleFrequency.WEEKLY,
         DeliveryMethod.EMAIL, {"recipients": ["analytics@example.com"]}),
        ("Monthly Executive", templates[2].template_id, ScheduleFrequency.MONTHLY,
         DeliveryMethod.EMAIL, {"recipients": ["ceo@example.com", "cfo@example.com"]}),
        ("Quarterly Compliance", templates[3].template_id, ScheduleFrequency.QUARTERLY,
         DeliveryMethod.SFTP, {"path": "/reports/compliance/"})
    ]
    
    schedules = []
    for name, tpl_id, freq, method, config in schedules_data:
        schedule = await generator.create_schedule(tpl_id, name, freq, method, config)
        schedules.append(schedule)
        print(f"  📅 {name} ({freq.value}) -> {method.value}")
        
    # Run some schedules
    print("\n▶️ Running Schedules...")
    
    for schedule in schedules[:2]:
        for _ in range(random.randint(3, 7)):
            report = await generator.run_schedule(schedule.schedule_id)
            
    for schedule in schedules[:2]:
        status = generator.get_schedule_status(schedule.schedule_id)
        print(f"  📅 {status['name']}: {status['run_count']} runs, {status['success_rate']:.0f}% success")
        
    # Report list
    print("\n📋 Recent Reports:")
    
    print("\n  ┌────────────────────────────────────────────┬────────────┬──────────────┬──────────┐")
    print("  │ Report                                     │ Format     │ Status       │ Size     │")
    print("  ├────────────────────────────────────────────┼────────────┼──────────────┼──────────┤")
    
    for report in generator.get_report_history()[:10]:
        name = report.name[:40].ljust(40)
        format_str = report.format.value.ljust(10)
        status = report.status.value.ljust(12)
        size = f"{report.file_size_bytes / 1024:.1f}KB" if report.file_size_bytes > 0 else "N/A"
        size = size.ljust(8)
        
        print(f"  │ {name} │ {format_str} │ {status} │ {size} │")
        
    print("  └────────────────────────────────────────────┴────────────┴──────────────┴──────────┘")
    
    # Template usage
    print("\n📝 Template Usage:")
    
    print("\n  ┌──────────────────────────────────┬─────────────────┬──────────────┬────────────┐")
    print("  │ Template                         │ Type            │ Reports      │ Sources    │")
    print("  ├──────────────────────────────────┼─────────────────┼──────────────┼────────────┤")
    
    for template in templates:
        name = template.name[:32].ljust(32)
        t_type = template.report_type.value[:15].ljust(15)
        count = str(template.generation_count).ljust(12)
        sources_count = str(len(template.data_sources)).ljust(10)
        
        print(f"  │ {name} │ {t_type} │ {count} │ {sources_count} │")
        
    print("  └──────────────────────────────────┴─────────────────┴──────────────┴────────────┘")
    
    # Schedule status
    print("\n📅 Schedule Status:")
    
    for schedule in schedules:
        status = generator.get_schedule_status(schedule.schedule_id)
        
        active = "✓" if status['is_active'] else "✗"
        next_run = status['next_run'][:16] if status['next_run'] else "N/A"
        
        print(f"\n  [{active}] {status['name']}")
        print(f"      Frequency: {status['frequency']} | Method: {status['delivery_method']}")
        print(f"      Runs: {status['run_count']} | Success: {status['success_rate']:.0f}%")
        print(f"      Next Run: {next_run}")
        
    # Search reports
    print("\n🔍 Search Results:")
    
    pdf_reports = generator.search_reports(format=ReportFormat.PDF)
    print(f"  PDF Reports: {len(pdf_reports)}")
    
    completed_reports = generator.search_reports(status=ReportStatus.COMPLETED)
    print(f"  Completed Reports: {len(completed_reports)}")
    
    ops_reports = generator.search_reports(template_id=templates[0].template_id)
    print(f"  Operations Reports: {len(ops_reports)}")
    
    # Report formats distribution
    print("\n📊 Format Distribution:")
    
    stats = generator.get_statistics()
    
    for format_name, count in stats['by_format'].items():
        bar = "█" * min(count, 15) + "░" * (15 - min(count, 15))
        print(f"  {format_name:8} [{bar}] {count}")
        
    # Status distribution
    print("\n📊 Status Distribution:")
    
    for status_name, count in stats['by_status'].items():
        bar = "█" * min(count, 15) + "░" * (15 - min(count, 15))
        icon = "✓" if status_name == "completed" else "✗" if status_name == "failed" else "○"
        print(f"  {icon} {status_name:12} [{bar}] {count}")
        
    # Statistics
    print("\n📊 Generator Statistics:")
    
    print(f"\n  Templates: {stats['total_templates']}")
    print("  By Type:")
    for t_type, count in stats['by_type'].items():
        print(f"    {t_type}: {count}")
        
    print(f"\n  Reports: {stats['total_reports']}")
    print(f"  Total Size: {stats['total_size_mb']:.1f} MB")
    print(f"  Avg Generation Time: {stats['avg_generation_time']:.2f}s")
    
    print(f"\n  Schedules: {stats['total_schedules']}")
    print(f"  Active Schedules: {stats['active_schedules']}")
    
    print(f"\n  Deliveries: {stats['total_deliveries']}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    Report Generator Platform                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Templates:             {stats['total_templates']:>12}                          │")
    print(f"│ Total Reports Generated:     {stats['total_reports']:>12}                          │")
    print(f"│ Total Storage Used:          {stats['total_size_mb']:>10.1f} MB                        │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Active Schedules:            {stats['active_schedules']:>12}                          │")
    print(f"│ Total Deliveries:            {stats['total_deliveries']:>12}                          │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("Report Generator Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
