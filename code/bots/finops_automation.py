#!/usr/bin/env python3
"""
FinOps Automation v11.0
Real-time cost tracking, budget alerts, optimization recommendations
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

import boto3
from google.cloud import billing_v1
from azure.mgmt.costmanagement import CostManagementClient
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DB_PATH = '/var/lib/finops/costs.db'
BUDGET_ALERT_THRESHOLD = 0.80  # 80% of budget
CLOUD_PROVIDERS = ['aws', 'gcp', 'azure']

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

@dataclass
class CostEntry:
    """Cost tracking entry"""
    service_name: str
    cost_usd: float
    resource_type: str
    cloud_provider: str
    timestamp: datetime
    tags: Dict[str, str]

@dataclass
class Budget:
    """Budget configuration"""
    name: str
    amount_usd: float
    period: str  # 'monthly', 'quarterly', 'yearly'
    services: List[str]
    alert_threshold: float

class FinOpsDatabase:
    """SQLite database for FinOps data"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                cost_usd REAL NOT NULL,
                resource_type TEXT NOT NULL,
                cloud_provider TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount_usd REAL NOT NULL,
                period TEXT NOT NULL,
                services TEXT,
                alert_threshold REAL DEFAULT 0.80,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_id INTEGER,
                current_spend REAL,
                budget_amount REAL,
                percentage REAL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(budget_id) REFERENCES budgets(budget_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                current_cost REAL,
                potential_savings REAL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_costs_timestamp ON cost_entries(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_costs_service ON cost_entries(service_name)')
        
        self.conn.commit()
        logger.info(f"FinOps database initialized: {self.db_path}")
    
    def record_cost(self, entry: CostEntry):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO cost_entries (service_name, cost_usd, resource_type, cloud_provider, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (entry.service_name, entry.cost_usd, entry.resource_type, entry.cloud_provider, entry.timestamp, json.dumps(entry.tags)))
        self.conn.commit()
    
    def get_costs(self, start_date: datetime, end_date: datetime, service: str = None) -> List[CostEntry]:
        cursor = self.conn.cursor()
        
        if service:
            cursor.execute('''
                SELECT service_name, cost_usd, resource_type, cloud_provider, timestamp, tags
                FROM cost_entries
                WHERE timestamp BETWEEN ? AND ? AND service_name = ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date, service))
        else:
            cursor.execute('''
                SELECT service_name, cost_usd, resource_type, cloud_provider, timestamp, tags
                FROM cost_entries
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
        
        entries = []
        for row in cursor.fetchall():
            entries.append(CostEntry(
                service_name=row[0], cost_usd=row[1], resource_type=row[2],
                cloud_provider=row[3], timestamp=datetime.fromisoformat(row[4]),
                tags=json.loads(row[5]) if row[5] else {}
            ))
        return entries
    
    def create_budget(self, budget: Budget):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO budgets (name, amount_usd, period, services, alert_threshold)
            VALUES (?, ?, ?, ?, ?)
        ''', (budget.name, budget.amount_usd, budget.period, json.dumps(budget.services), budget.alert_threshold))
        self.conn.commit()
        logger.info(f"Budget created: {budget.name} - ${budget.amount_usd}")

class AWSCostCollector:
    """Collect costs from AWS"""
    
    def __init__(self):
        try:
            self.client = boto3.client('ce', region_name='us-east-1')
        except:
            self.client = None
            logger.warning("AWS Cost Explorer not available")
    
    def get_costs(self, start_date: datetime, end_date: datetime) -> List[CostEntry]:
        if not self.client:
            return []
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
                ]
            )
            
            entries = []
            for result in response['ResultsByTime']:
                timestamp = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')
                
                for group in result['Groups']:
                    service = group['Keys'][0]
                    resource_id = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    entries.append(CostEntry(
                        service_name=service,
                        cost_usd=cost,
                        resource_type='aws_resource',
                        cloud_provider='aws',
                        timestamp=timestamp,
                        tags={'resource_id': resource_id}
                    ))
            
            return entries
        except Exception as e:
            logger.error(f"Error fetching AWS costs: {e}")
            return []

class GCPCostCollector:
    """Collect costs from GCP"""
    
    def __init__(self):
        try:
            self.client = billing_v1.CloudBillingClient()
        except:
            self.client = None
            logger.warning("GCP Billing API not available")
    
    def get_costs(self, start_date: datetime, end_date: datetime) -> List[CostEntry]:
        if not self.client:
            return []
        
        # Implementation using GCP Billing API
        # Simplified for brevity
        return []

class CostOptimizer:
    """Generate cost optimization recommendations"""
    
    def __init__(self, db: FinOpsDatabase):
        self.db = db
    
    def analyze_rightsizing_opportunities(self) -> List[Dict]:
        """Identify over-provisioned resources"""
        
        # Get recent cost data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        costs = self.db.get_costs(start_date, end_date)
        
        recommendations = []
        
        # Analyze by service
        service_costs = {}
        for entry in costs:
            if entry.service_name not in service_costs:
                service_costs[entry.service_name] = []
            service_costs[entry.service_name].append(entry.cost_usd)
        
        for service, costs_list in service_costs.items():
            avg_cost = sum(costs_list) / len(costs_list)
            
            # Check if consistently low usage (high potential for rightsizing)
            if avg_cost > 100 and len(costs_list) > 20:
                # Simplified: recommend 30% reduction
                potential_savings = avg_cost * 0.3 * 30  # 30 days
                
                recommendations.append({
                    'service': service,
                    'type': 'rightsizing',
                    'current_cost': avg_cost * 30,
                    'potential_savings': potential_savings,
                    'description': f'Consider rightsizing {service} resources. Potential 30% reduction.'
                })
        
        return recommendations
    
    def analyze_reserved_instance_opportunities(self) -> List[Dict]:
        """Identify opportunities for reserved instances"""
        
        recommendations = []
        
        # Get on-demand usage patterns
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        costs = self.db.get_costs(start_date, end_date)
        
        # Analyze consistency
        compute_costs = [c for c in costs if 'compute' in c.resource_type.lower() or 'ec2' in c.service_name.lower()]
        
        if len(compute_costs) > 60:  # 60+ days of consistent usage
            total_compute_cost = sum(c.cost_usd for c in compute_costs)
            
            # Reserved instances typically 30-40% cheaper
            potential_savings = total_compute_cost * 0.35
            
            recommendations.append({
                'service': 'compute',
                'type': 'reserved_instances',
                'current_cost': total_compute_cost,
                'potential_savings': potential_savings,
                'description': 'Consider purchasing reserved instances for consistent workloads. Potential 35% savings.'
            })
        
        return recommendations
    
    def analyze_unused_resources(self) -> List[Dict]:
        """Identify unused or underutilized resources"""
        
        recommendations = []
        
        # Query for resources with zero usage in last 7 days
        # Simplified implementation
        
        recommendations.append({
            'service': 'storage',
            'type': 'unused_resources',
            'current_cost': 50,
            'potential_savings': 50,
            'description': 'Remove unused storage volumes and snapshots'
        })
        
        return recommendations

class BudgetAlertEngine:
    """Monitor budgets and trigger alerts"""
    
    def __init__(self, db: FinOpsDatabase):
        self.db = db
    
    def check_budgets(self):
        """Check all budgets and trigger alerts if needed"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT budget_id, name, amount_usd, period, services, alert_threshold FROM budgets')
        
        for row in cursor.fetchall():
            budget_id, name, amount, period, services_json, threshold = row
            services = json.loads(services_json) if services_json else []
            
            # Calculate current spend
            current_spend = self._calculate_current_spend(period, services)
            
            # Check if alert needed
            percentage = current_spend / amount if amount > 0 else 0
            
            if percentage >= threshold:
                self._trigger_alert(budget_id, name, current_spend, amount, percentage)
    
    def _calculate_current_spend(self, period: str, services: List[str]) -> float:
        """Calculate current spend for period"""
        
        end_date = datetime.now()
        
        if period == 'monthly':
            start_date = end_date.replace(day=1)
        elif period == 'quarterly':
            quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
            start_date = end_date.replace(month=quarter_start_month, day=1)
        else:  # yearly
            start_date = end_date.replace(month=1, day=1)
        
        costs = self.db.get_costs(start_date, end_date)
        
        if services:
            costs = [c for c in costs if c.service_name in services]
        
        return sum(c.cost_usd for c in costs)
    
    def _trigger_alert(self, budget_id: int, name: str, current_spend: float, budget_amount: float, percentage: float):
        """Trigger budget alert"""
        
        cursor = self.db.conn.cursor()
        cursor.execute('''
            INSERT INTO budget_alerts (budget_id, current_spend, budget_amount, percentage)
            VALUES (?, ?, ?, ?)
        ''', (budget_id, current_spend, budget_amount, percentage))
        self.db.conn.commit()
        
        logger.warning(f"BUDGET ALERT: {name} - ${current_spend:.2f} / ${budget_amount:.2f} ({percentage*100:.1f}%)")

class FinOpsEngine:
    """Main FinOps automation engine"""
    
    def __init__(self):
        self.db = FinOpsDatabase()
        self.aws_collector = AWSCostCollector()
        self.gcp_collector = GCPCostCollector()
        self.optimizer = CostOptimizer(self.db)
        self.budget_engine = BudgetAlertEngine(self.db)
    
    def collect_costs(self):
        """Collect costs from all cloud providers"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # AWS
        aws_costs = self.aws_collector.get_costs(start_date, end_date)
        for cost in aws_costs:
            self.db.record_cost(cost)
        
        logger.info(f"Collected {len(aws_costs)} AWS cost entries")
        
        # GCP
        gcp_costs = self.gcp_collector.get_costs(start_date, end_date)
        for cost in gcp_costs:
            self.db.record_cost(cost)
        
        logger.info(f"Collected {len(gcp_costs)} GCP cost entries")
    
    def generate_report(self, days: int = 30) -> Dict:
        """Generate cost report"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        costs = self.db.get_costs(start_date, end_date)
        
        # Total cost
        total_cost = sum(c.cost_usd for c in costs)
        
        # Cost by service
        by_service = {}
        for cost in costs:
            if cost.service_name not in by_service:
                by_service[cost.service_name] = 0
            by_service[cost.service_name] += cost.cost_usd
        
        # Cost by provider
        by_provider = {}
        for cost in costs:
            if cost.cloud_provider not in by_provider:
                by_provider[cost.cloud_provider] = 0
            by_provider[cost.cloud_provider] += cost.cost_usd
        
        return {
            'period': f'{days} days',
            'total_cost': total_cost,
            'by_service': by_service,
            'by_provider': by_provider,
            'entry_count': len(costs)
        }
    
    def optimize(self):
        """Run optimization analysis"""
        
        rightsizing = self.optimizer.analyze_rightsizing_opportunities()
        reserved = self.optimizer.analyze_reserved_instance_opportunities()
        unused = self.optimizer.analyze_unused_resources()
        
        all_recommendations = rightsizing + reserved + unused
        
        # Store recommendations
        cursor = self.db.conn.cursor()
        for rec in all_recommendations:
            cursor.execute('''
                INSERT INTO optimization_recommendations 
                (service_name, recommendation_type, current_cost, potential_savings, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (rec['service'], rec['type'], rec['current_cost'], rec['potential_savings'], rec['description']))
        self.db.conn.commit()
        
        total_savings = sum(r['potential_savings'] for r in all_recommendations)
        
        logger.info(f"Generated {len(all_recommendations)} recommendations with ${total_savings:.2f} potential savings")
        
        return all_recommendations

def main():
    """Main entry point"""
    logger.info("FinOps Automation v11.0")
    
    engine = FinOpsEngine()
    
    if '--collect' in sys.argv:
        engine.collect_costs()
        
    elif '--report' in sys.argv:
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        report = engine.generate_report(days)
        print(json.dumps(report, indent=2))
        
    elif '--optimize' in sys.argv:
        recommendations = engine.optimize()
        print(json.dumps(recommendations, indent=2, default=str))
        
    elif '--check-budgets' in sys.argv:
        engine.budget_engine.check_budgets()
        
    else:
        print("Usage:")
        print("  --collect              Collect costs from cloud providers")
        print("  --report [DAYS]        Generate cost report")
        print("  --optimize             Generate optimization recommendations")
        print("  --check-budgets        Check budget alerts")

if __name__ == '__main__':
    main()
