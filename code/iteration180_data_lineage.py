#!/usr/bin/env python3
"""
Server Init - Iteration 180: Data Lineage Platform
Платформа отслеживания происхождения данных

Функционал:
- Lineage Tracking - отслеживание происхождения
- Data Flow Visualization - визуализация потоков данных
- Impact Analysis - анализ влияния
- Column-Level Lineage - линейность на уровне колонок
- Source Discovery - обнаружение источников
- Transformation Tracking - отслеживание трансформаций
- Data Quality Integration - интеграция с качеством данных
- Compliance Reporting - отчётность для соответствия
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import uuid


class NodeType(Enum):
    """Тип узла"""
    DATABASE = "database"
    TABLE = "table"
    COLUMN = "column"
    FILE = "file"
    API = "api"
    STREAM = "stream"
    DASHBOARD = "dashboard"
    REPORT = "report"
    MODEL = "model"
    TRANSFORMATION = "transformation"


class EdgeType(Enum):
    """Тип связи"""
    DERIVES_FROM = "derives_from"
    FEEDS_INTO = "feeds_into"
    TRANSFORMS = "transforms"
    AGGREGATES = "aggregates"
    JOINS = "joins"
    FILTERS = "filters"
    COPIES = "copies"


class DataClassification(Enum):
    """Классификация данных"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"


class ChangeType(Enum):
    """Тип изменения"""
    SCHEMA_CHANGE = "schema_change"
    DATA_CHANGE = "data_change"
    TRANSFORMATION_CHANGE = "transformation_change"
    SOURCE_CHANGE = "source_change"


@dataclass
class LineageNode:
    """Узел линейности"""
    node_id: str
    name: str = ""
    description: str = ""
    
    # Type
    node_type: NodeType = NodeType.TABLE
    
    # Location
    system: str = ""  # Database, warehouse, etc.
    schema_name: str = ""
    
    # Classification
    classification: DataClassification = DataClassification.INTERNAL
    
    # Metadata
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    # Quality
    quality_score: float = 100.0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LineageEdge:
    """Связь линейности"""
    edge_id: str
    
    # Connection
    source_id: str = ""
    target_id: str = ""
    
    # Type
    edge_type: EdgeType = EdgeType.DERIVES_FROM
    
    # Transformation
    transformation_logic: str = ""
    sql_query: str = ""
    
    # Job info
    job_id: str = ""
    job_name: str = ""
    
    # Timing
    last_run: Optional[datetime] = None
    run_frequency: str = ""  # hourly, daily, etc.


@dataclass
class ColumnLineage:
    """Линейность на уровне колонок"""
    column_id: str
    
    # Column info
    table_id: str = ""
    column_name: str = ""
    data_type: str = ""
    
    # Source columns
    source_columns: List[str] = field(default_factory=list)  # column_ids
    
    # Transformation
    transformation: str = ""  # SQL expression, function, etc.
    
    # Classification
    is_pii: bool = False
    is_sensitive: bool = False


@dataclass
class ImpactAnalysis:
    """Анализ влияния"""
    analysis_id: str
    source_node_id: str = ""
    
    # Impact
    downstream_nodes: List[str] = field(default_factory=list)
    upstream_nodes: List[str] = field(default_factory=list)
    
    # By type
    impacted_tables: List[str] = field(default_factory=list)
    impacted_reports: List[str] = field(default_factory=list)
    impacted_dashboards: List[str] = field(default_factory=list)
    impacted_models: List[str] = field(default_factory=list)
    
    # Risk
    risk_level: str = "low"  # low, medium, high, critical
    affected_systems: List[str] = field(default_factory=list)
    
    # Generated
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataFlow:
    """Поток данных"""
    flow_id: str
    name: str = ""
    description: str = ""
    
    # Flow path
    nodes: List[str] = field(default_factory=list)  # Ordered list of node_ids
    edges: List[str] = field(default_factory=list)
    
    # Schedule
    schedule: str = ""
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # Status
    status: str = "active"  # active, paused, failed


class LineageGraph:
    """Граф линейности"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
        self.column_lineage: Dict[str, ColumnLineage] = {}
        
        # Index for fast lookup
        self.outgoing: Dict[str, Set[str]] = {}  # node_id -> set of edge_ids
        self.incoming: Dict[str, Set[str]] = {}
        
    def add_node(self, node: LineageNode):
        """Добавление узла"""
        self.nodes[node.node_id] = node
        if node.node_id not in self.outgoing:
            self.outgoing[node.node_id] = set()
        if node.node_id not in self.incoming:
            self.incoming[node.node_id] = set()
            
    def add_edge(self, edge: LineageEdge):
        """Добавление связи"""
        self.edges[edge.edge_id] = edge
        
        if edge.source_id not in self.outgoing:
            self.outgoing[edge.source_id] = set()
        self.outgoing[edge.source_id].add(edge.edge_id)
        
        if edge.target_id not in self.incoming:
            self.incoming[edge.target_id] = set()
        self.incoming[edge.target_id].add(edge.edge_id)
        
    def get_upstream(self, node_id: str, max_depth: int = 10) -> List[str]:
        """Получение upstream узлов"""
        visited = set()
        result = []
        
        def traverse(nid: str, depth: int):
            if depth > max_depth or nid in visited:
                return
            visited.add(nid)
            
            for edge_id in self.incoming.get(nid, []):
                edge = self.edges.get(edge_id)
                if edge:
                    result.append(edge.source_id)
                    traverse(edge.source_id, depth + 1)
                    
        traverse(node_id, 0)
        return result
        
    def get_downstream(self, node_id: str, max_depth: int = 10) -> List[str]:
        """Получение downstream узлов"""
        visited = set()
        result = []
        
        def traverse(nid: str, depth: int):
            if depth > max_depth or nid in visited:
                return
            visited.add(nid)
            
            for edge_id in self.outgoing.get(nid, []):
                edge = self.edges.get(edge_id)
                if edge:
                    result.append(edge.target_id)
                    traverse(edge.target_id, depth + 1)
                    
        traverse(node_id, 0)
        return result


class LineageCollector:
    """Сборщик линейности"""
    
    def __init__(self, graph: LineageGraph):
        self.graph = graph
        
    async def collect_from_sql(self, sql: str, job_id: str = "") -> List[LineageEdge]:
        """Сбор линейности из SQL"""
        # Simulate SQL parsing
        await asyncio.sleep(0.02)
        
        edges = []
        # In real implementation, would parse SQL to extract lineage
        
        return edges
        
    async def collect_from_etl(self, job_config: Dict) -> List[LineageEdge]:
        """Сбор линейности из ETL конфигурации"""
        await asyncio.sleep(0.02)
        
        edges = []
        sources = job_config.get("sources", [])
        targets = job_config.get("targets", [])
        
        for source in sources:
            for target in targets:
                edge = LineageEdge(
                    edge_id=f"edge_{uuid.uuid4().hex[:8]}",
                    source_id=source,
                    target_id=target,
                    edge_type=EdgeType.TRANSFORMS,
                    job_id=job_config.get("job_id", ""),
                    job_name=job_config.get("job_name", ""),
                    last_run=datetime.now()
                )
                edges.append(edge)
                self.graph.add_edge(edge)
                
        return edges


class ImpactAnalyzer:
    """Анализатор влияния"""
    
    def __init__(self, graph: LineageGraph):
        self.graph = graph
        
    def analyze(self, node_id: str) -> ImpactAnalysis:
        """Анализ влияния изменения"""
        analysis = ImpactAnalysis(
            analysis_id=f"impact_{uuid.uuid4().hex[:8]}",
            source_node_id=node_id
        )
        
        # Get downstream
        downstream = self.graph.get_downstream(node_id)
        analysis.downstream_nodes = downstream
        
        # Get upstream
        upstream = self.graph.get_upstream(node_id)
        analysis.upstream_nodes = upstream
        
        # Categorize by type
        for nid in downstream:
            node = self.graph.nodes.get(nid)
            if node:
                if node.node_type == NodeType.TABLE:
                    analysis.impacted_tables.append(nid)
                elif node.node_type == NodeType.REPORT:
                    analysis.impacted_reports.append(nid)
                elif node.node_type == NodeType.DASHBOARD:
                    analysis.impacted_dashboards.append(nid)
                elif node.node_type == NodeType.MODEL:
                    analysis.impacted_models.append(nid)
                    
                if node.system not in analysis.affected_systems:
                    analysis.affected_systems.append(node.system)
                    
        # Determine risk level
        total_impacted = len(downstream)
        if total_impacted > 50:
            analysis.risk_level = "critical"
        elif total_impacted > 20:
            analysis.risk_level = "high"
        elif total_impacted > 5:
            analysis.risk_level = "medium"
        else:
            analysis.risk_level = "low"
            
        return analysis


class DataFlowManager:
    """Менеджер потоков данных"""
    
    def __init__(self, graph: LineageGraph):
        self.graph = graph
        self.flows: Dict[str, DataFlow] = {}
        
    def create_flow(self, name: str, node_path: List[str]) -> DataFlow:
        """Создание потока"""
        flow = DataFlow(
            flow_id=f"flow_{uuid.uuid4().hex[:8]}",
            name=name,
            nodes=node_path
        )
        
        # Build edges
        for i in range(len(node_path) - 1):
            source = node_path[i]
            target = node_path[i + 1]
            
            # Find edge
            for edge_id in self.graph.outgoing.get(source, []):
                edge = self.graph.edges.get(edge_id)
                if edge and edge.target_id == target:
                    flow.edges.append(edge_id)
                    break
                    
        self.flows[flow.flow_id] = flow
        return flow
        
    def visualize_flow(self, flow_id: str) -> str:
        """Визуализация потока"""
        flow = self.flows.get(flow_id)
        if not flow:
            return ""
            
        lines = []
        for i, node_id in enumerate(flow.nodes):
            node = self.graph.nodes.get(node_id)
            if node:
                prefix = "  " * i
                lines.append(f"{prefix}└── {node.name} ({node.node_type.value})")
                
        return "\n".join(lines)


class LineageReporter:
    """Генератор отчётов линейности"""
    
    def __init__(self, graph: LineageGraph):
        self.graph = graph
        
    def generate_node_report(self, node_id: str) -> Dict[str, Any]:
        """Отчёт по узлу"""
        node = self.graph.nodes.get(node_id)
        if not node:
            return {}
            
        upstream = self.graph.get_upstream(node_id)
        downstream = self.graph.get_downstream(node_id)
        
        return {
            "node_id": node_id,
            "name": node.name,
            "type": node.node_type.value,
            "system": node.system,
            "classification": node.classification.value,
            "upstream_count": len(upstream),
            "downstream_count": len(downstream),
            "quality_score": node.quality_score,
            "tags": node.tags
        }


class DataLineagePlatform:
    """Платформа отслеживания происхождения данных"""
    
    def __init__(self):
        self.graph = LineageGraph()
        self.collector = LineageCollector(self.graph)
        self.analyzer = ImpactAnalyzer(self.graph)
        self.flow_manager = DataFlowManager(self.graph)
        self.reporter = LineageReporter(self.graph)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        nodes = list(self.graph.nodes.values())
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(self.graph.edges),
            "nodes_by_type": {
                ntype.value: len([n for n in nodes if n.node_type == ntype])
                for ntype in NodeType
            },
            "total_flows": len(self.flow_manager.flows),
            "column_lineage_count": len(self.graph.column_lineage)
        }


# Демонстрация
if __name__ == "__main__":
    print("=" * 60)
    print("Server Init - Iteration 180: Data Lineage Platform")
    print("=" * 60)
    
    async def demo():
        platform = DataLineagePlatform()
        print("✓ Data Lineage Platform created")
        
        # Create data sources
        print("\n📊 Creating Data Sources...")
        
        sources = [
            LineageNode(
                node_id="src_crm",
                name="CRM Database",
                node_type=NodeType.DATABASE,
                system="salesforce",
                owner="sales-team"
            ),
            LineageNode(
                node_id="src_erp",
                name="ERP System",
                node_type=NodeType.DATABASE,
                system="sap",
                owner="finance-team"
            ),
            LineageNode(
                node_id="src_web",
                name="Web Analytics",
                node_type=NodeType.STREAM,
                system="google-analytics",
                owner="marketing-team"
            ),
        ]
        
        for node in sources:
            platform.graph.add_node(node)
            print(f"  ✓ {node.name} ({node.node_type.value})")
            
        # Create tables
        print("\n📋 Creating Tables...")
        
        tables = [
            LineageNode(
                node_id="tbl_customers",
                name="customers",
                node_type=NodeType.TABLE,
                system="warehouse",
                schema_name="raw",
                classification=DataClassification.PII
            ),
            LineageNode(
                node_id="tbl_orders",
                name="orders",
                node_type=NodeType.TABLE,
                system="warehouse",
                schema_name="raw"
            ),
            LineageNode(
                node_id="tbl_products",
                name="products",
                node_type=NodeType.TABLE,
                system="warehouse",
                schema_name="raw"
            ),
            LineageNode(
                node_id="tbl_customer_360",
                name="customer_360",
                node_type=NodeType.TABLE,
                system="warehouse",
                schema_name="analytics",
                classification=DataClassification.PII
            ),
            LineageNode(
                node_id="tbl_sales_summary",
                name="sales_summary",
                node_type=NodeType.TABLE,
                system="warehouse",
                schema_name="analytics"
            ),
        ]
        
        for table in tables:
            platform.graph.add_node(table)
            print(f"  ✓ {table.schema_name}.{table.name}")
            
        # Create outputs
        print("\n📈 Creating Outputs...")
        
        outputs = [
            LineageNode(
                node_id="dash_sales",
                name="Sales Dashboard",
                node_type=NodeType.DASHBOARD,
                system="tableau",
                owner="bi-team"
            ),
            LineageNode(
                node_id="report_revenue",
                name="Revenue Report",
                node_type=NodeType.REPORT,
                system="looker",
                owner="finance-team"
            ),
            LineageNode(
                node_id="model_churn",
                name="Churn Prediction Model",
                node_type=NodeType.MODEL,
                system="mlflow",
                owner="data-science"
            ),
        ]
        
        for output in outputs:
            platform.graph.add_node(output)
            print(f"  ✓ {output.name} ({output.node_type.value})")
            
        # Create lineage edges
        print("\n🔗 Creating Lineage Connections...")
        
        edges = [
            # Sources to raw tables
            LineageEdge(edge_id="e1", source_id="src_crm", target_id="tbl_customers", edge_type=EdgeType.FEEDS_INTO, job_name="crm_sync"),
            LineageEdge(edge_id="e2", source_id="src_erp", target_id="tbl_orders", edge_type=EdgeType.FEEDS_INTO, job_name="erp_sync"),
            LineageEdge(edge_id="e3", source_id="src_erp", target_id="tbl_products", edge_type=EdgeType.FEEDS_INTO, job_name="erp_sync"),
            LineageEdge(edge_id="e4", source_id="src_web", target_id="tbl_customers", edge_type=EdgeType.FEEDS_INTO, job_name="web_events"),
            # Raw to analytics
            LineageEdge(edge_id="e5", source_id="tbl_customers", target_id="tbl_customer_360", edge_type=EdgeType.TRANSFORMS, job_name="customer_etl"),
            LineageEdge(edge_id="e6", source_id="tbl_orders", target_id="tbl_customer_360", edge_type=EdgeType.JOINS, job_name="customer_etl"),
            LineageEdge(edge_id="e7", source_id="tbl_orders", target_id="tbl_sales_summary", edge_type=EdgeType.AGGREGATES, job_name="sales_agg"),
            LineageEdge(edge_id="e8", source_id="tbl_products", target_id="tbl_sales_summary", edge_type=EdgeType.JOINS, job_name="sales_agg"),
            # Analytics to outputs
            LineageEdge(edge_id="e9", source_id="tbl_sales_summary", target_id="dash_sales", edge_type=EdgeType.FEEDS_INTO),
            LineageEdge(edge_id="e10", source_id="tbl_sales_summary", target_id="report_revenue", edge_type=EdgeType.FEEDS_INTO),
            LineageEdge(edge_id="e11", source_id="tbl_customer_360", target_id="dash_sales", edge_type=EdgeType.FEEDS_INTO),
            LineageEdge(edge_id="e12", source_id="tbl_customer_360", target_id="model_churn", edge_type=EdgeType.FEEDS_INTO),
        ]
        
        for edge in edges:
            platform.graph.add_edge(edge)
            src = platform.graph.nodes.get(edge.source_id)
            tgt = platform.graph.nodes.get(edge.target_id)
            print(f"  {src.name if src else edge.source_id} → {tgt.name if tgt else edge.target_id}")
            
        # Show lineage
        print("\n🌳 Lineage Graph:")
        
        print("\n  Data Sources:")
        for src in sources:
            downstream = platform.graph.get_downstream(src.node_id)
            print(f"    {src.name} → {len(downstream)} downstream nodes")
            
        print("\n  Data Outputs:")
        for out in outputs:
            upstream = platform.graph.get_upstream(out.node_id)
            print(f"    {out.name} ← {len(upstream)} upstream nodes")
            
        # Impact analysis
        print("\n⚡ Impact Analysis:")
        
        # Analyze impact of changing customers table
        analysis = platform.analyzer.analyze("tbl_customers")
        
        print(f"\n  Source: customers table")
        print(f"  Risk Level: {analysis.risk_level.upper()}")
        print(f"  Downstream Impact: {len(analysis.downstream_nodes)} nodes")
        print(f"  Upstream Sources: {len(analysis.upstream_nodes)} nodes")
        
        print("\n  Impacted Assets:")
        print(f"    Tables: {len(analysis.impacted_tables)}")
        print(f"    Reports: {len(analysis.impacted_reports)}")
        print(f"    Dashboards: {len(analysis.impacted_dashboards)}")
        print(f"    Models: {len(analysis.impacted_models)}")
        
        print(f"\n  Affected Systems: {', '.join(analysis.affected_systems)}")
        
        # Create data flow
        print("\n🔄 Creating Data Flow...")
        
        flow = platform.flow_manager.create_flow(
            "Customer Analytics Pipeline",
            ["src_crm", "tbl_customers", "tbl_customer_360", "model_churn"]
        )
        
        print(f"\n  Flow: {flow.name}")
        print(f"  Nodes: {len(flow.nodes)}")
        print(f"  Edges: {len(flow.edges)}")
        
        print("\n  Flow Visualization:")
        viz = platform.flow_manager.visualize_flow(flow.flow_id)
        print(viz)
        
        # Node report
        print("\n📄 Node Reports:")
        
        for node_id in ["tbl_customer_360", "dash_sales"]:
            report = platform.reporter.generate_node_report(node_id)
            print(f"\n  {report['name']}:")
            print(f"    Type: {report['type']}")
            print(f"    System: {report['system']}")
            print(f"    Classification: {report['classification']}")
            print(f"    Upstream: {report['upstream_count']}, Downstream: {report['downstream_count']}")
            
        # Lineage summary
        print("\n📊 Lineage Summary:")
        
        print("\n  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐")
        print("  │ Node                         │ Type          │ System      │ Upstream │ Downstream │")
        print("  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤")
        
        for node in platform.graph.nodes.values():
            name = node.name[:28].ljust(28)
            ntype = node.node_type.value[:13].ljust(13)
            system = node.system[:11].ljust(11)
            up = len(platform.graph.get_upstream(node.node_id))
            down = len(platform.graph.get_downstream(node.node_id))
            print(f"  │ {name} │ {ntype} │ {system} │ {up:>8} │ {down:>10} │")
            
        print("  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘")
        
        # Platform statistics
        print("\n📈 Platform Statistics:")
        
        stats = platform.get_statistics()
        
        print(f"\n  Total Nodes: {stats['total_nodes']}")
        print(f"  Total Edges: {stats['total_edges']}")
        print(f"  Data Flows: {stats['total_flows']}")
        
        print("\n  Nodes by Type:")
        for ntype, count in stats['nodes_by_type'].items():
            if count > 0:
                print(f"    • {ntype}: {count}")
                
        # Dashboard
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│                    Data Lineage Dashboard                          │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Total Nodes:                 {stats['total_nodes']:>10}                       │")
        print(f"│ Total Edges:                 {stats['total_edges']:>10}                       │")
        print(f"│ Data Flows:                  {stats['total_flows']:>10}                       │")
        print("├────────────────────────────────────────────────────────────────────┤")
        print(f"│ Databases:                   {stats['nodes_by_type'].get('database', 0):>10}                       │")
        print(f"│ Tables:                      {stats['nodes_by_type'].get('table', 0):>10}                       │")
        print(f"│ Dashboards:                  {stats['nodes_by_type'].get('dashboard', 0):>10}                       │")
        print(f"│ Models:                      {stats['nodes_by_type'].get('model', 0):>10}                       │")
        print("└────────────────────────────────────────────────────────────────────┘")
        
    asyncio.run(demo())
    
    print("\n" + "=" * 60)
    print("Data Lineage Platform initialized!")
    print("=" * 60)
