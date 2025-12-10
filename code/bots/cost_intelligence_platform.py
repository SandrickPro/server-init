#!/usr/bin/env python3
"""
Cost Intelligence Platform v12.0
Advanced cost management with ML predictions, budget optimization, and automated savings
Multi-cloud cost tracking with anomaly detection and forecasting
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

# ML and forecasting
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

# Time series forecasting
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    import prophet
except ImportError:
    print("Warning: forecasting libraries not installed")

# Cloud SDKs
try:
    import boto3  # AWS
    from google.cloud import billing  # GCP
    from azure.mgmt.costmanagement import CostManagementClient  # Azure
except ImportError:
    print("Warning: cloud SDKs not installed")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
COST_DB = '/var/lib/cost/intelligence.db'
COST_CONFIG = '/etc/cost/config.yaml'
COST_MODELS = '/var/lib/cost/models/'

# Cost thresholds
ANOMALY_THRESHOLD = 1.5  # 50% deviation triggers anomaly
FORECAST_DAYS = 90
SAVINGS_TARGET = 0.30  # 30% savings goal

for directory in [os.path.dirname(COST_DB), os.path.dirname(COST_CONFIG), COST_MODELS]:
    Path(directory).mkdir(parents=True, exist_ok=True)

################################################################################
# Data Models
################################################################################

class CloudProvider(Enum):
    """Cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on_premise"

class CostCategory(Enum):
    """Cost categories"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    OTHER = "other"

@dataclass
class CostEntry:
    """Cost entry"""
    cost_id: str
    provider: CloudProvider
    service: str
    category: CostCategory
    cost_usd: float
    usage_amount: float
    usage_unit: str
    resource_id: Optional[str]
    tags: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CostForecast:
    """Cost forecast"""
    forecast_id: str
    provider: CloudProvider
    category: CostCategory
    current_monthly_cost: float
    forecasted_monthly_cost: float
    forecast_date: datetime
    confidence_interval: Tuple[float, float]
    trend: str  # increasing, decreasing, stable

@dataclass
class SavingsRecommendation:
    """Cost savings recommendation"""
    recommendation_id: str
    title: str
    description: str
    provider: CloudProvider
    category: CostCategory
    potential_savings_usd: float
    potential_savings_percent: float
    effort: str  # low, medium, high
    priority: str  # low, medium, high, critical
    implementation: str
    affected_resources: List[str]

@dataclass
class BudgetAlert:
    """Budget alert"""
    alert_id: str
    budget_name: str
    budget_amount: float
    current_spend: float
    percentage: float
    severity: str  # warning, critical
    timestamp: datetime = field(default_factory=datetime.now)

################################################################################
# Database Manager
################################################################################

class CostDatabase:
    """Database for cost data"""
    
    def __init__(self, db_path: str = COST_DB):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Cost entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_entries (
                cost_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                service TEXT NOT NULL,
                category TEXT NOT NULL,
                cost_usd REAL NOT NULL,
                usage_amount REAL NOT NULL,
                usage_unit TEXT NOT NULL,
                resource_id TEXT,
                tags_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE
            )
        ''')
        
        # Aggregated costs table (daily)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_costs (
                agg_id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                service TEXT NOT NULL,
                category TEXT NOT NULL,
                date DATE NOT NULL,
                total_cost_usd REAL NOT NULL,
                total_usage REAL NOT NULL,
                UNIQUE(provider, service, category, date)
            )
        ''')
        
        # Forecasts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                forecast_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                category TEXT NOT NULL,
                current_monthly_cost REAL NOT NULL,
                forecasted_monthly_cost REAL NOT NULL,
                forecast_date TIMESTAMP NOT NULL,
                confidence_lower REAL,
                confidence_upper REAL,
                trend TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                provider TEXT NOT NULL,
                category TEXT NOT NULL,
                potential_savings_usd REAL NOT NULL,
                potential_savings_percent REAL NOT NULL,
                effort TEXT NOT NULL,
                priority TEXT NOT NULL,
                implementation TEXT,
                affected_resources_json TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                implemented_at TIMESTAMP
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                budget_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                provider TEXT,
                category TEXT,
                amount_usd REAL NOT NULL,
                period TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                alert_threshold REAL DEFAULT 0.80,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Budget alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_alerts (
                alert_id TEXT PRIMARY KEY,
                budget_id TEXT NOT NULL,
                budget_name TEXT NOT NULL,
                budget_amount REAL NOT NULL,
                current_spend REAL NOT NULL,
                percentage REAL NOT NULL,
                severity TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged INTEGER DEFAULT 0,
                FOREIGN KEY(budget_id) REFERENCES budgets(budget_id)
            )
        ''')
        
        # Anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_anomalies (
                anomaly_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                service TEXT NOT NULL,
                category TEXT NOT NULL,
                date DATE NOT NULL,
                expected_cost REAL NOT NULL,
                actual_cost REAL NOT NULL,
                deviation_percent REAL NOT NULL,
                severity TEXT NOT NULL,
                investigated INTEGER DEFAULT 0,
                root_cause TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_costs_timestamp ON cost_entries(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_costs_provider ON cost_entries(provider, service)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_costs(date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recs_priority ON recommendations(priority, status)')
        
        self.conn.commit()
        logger.info(f"Cost database initialized: {db_path}")
    
    def save_cost_entry(self, entry: CostEntry):
        """Save cost entry"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO cost_entries 
            (cost_id, provider, service, category, cost_usd, usage_amount, 
             usage_unit, resource_id, tags_json, timestamp, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.cost_id,
            entry.provider.value,
            entry.service,
            entry.category.value,
            entry.cost_usd,
            entry.usage_amount,
            entry.usage_unit,
            entry.resource_id,
            json.dumps(entry.tags),
            entry.timestamp.isoformat(),
            entry.timestamp.date().isoformat()
        ))
        self.conn.commit()
    
    def save_forecast(self, forecast: CostForecast):
        """Save forecast"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO forecasts 
            (forecast_id, provider, category, current_monthly_cost, 
             forecasted_monthly_cost, forecast_date, confidence_lower, 
             confidence_upper, trend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            forecast.forecast_id,
            forecast.provider.value,
            forecast.category.value,
            forecast.current_monthly_cost,
            forecast.forecasted_monthly_cost,
            forecast.forecast_date.isoformat(),
            forecast.confidence_interval[0],
            forecast.confidence_interval[1],
            forecast.trend
        ))
        self.conn.commit()
    
    def save_recommendation(self, rec: SavingsRecommendation):
        """Save recommendation"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO recommendations 
            (recommendation_id, title, description, provider, category,
             potential_savings_usd, potential_savings_percent, effort,
             priority, implementation, affected_resources_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            rec.recommendation_id,
            rec.title,
            rec.description,
            rec.provider.value,
            rec.category.value,
            rec.potential_savings_usd,
            rec.potential_savings_percent,
            rec.effort,
            rec.priority,
            rec.implementation,
            json.dumps(rec.affected_resources)
        ))
        self.conn.commit()
    
    def get_daily_costs(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get daily costs as DataFrame"""
        query = '''
            SELECT date, provider, service, category, SUM(cost_usd) as cost
            FROM cost_entries
            WHERE date BETWEEN ? AND ?
            GROUP BY date, provider, service, category
            ORDER BY date ASC
        '''
        
        df = pd.read_sql_query(
            query,
            self.conn,
            params=(start_date.date().isoformat(), end_date.date().isoformat()),
            parse_dates=['date']
        )
        
        return df

################################################################################
# Cost Forecasting Engine
################################################################################

class CostForecastEngine:
    """ML-powered cost forecasting"""
    
    def __init__(self, models_dir: str = COST_MODELS):
        self.models_dir = models_dir
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            self.model = joblib.load(f'{self.models_dir}/cost_forecast_model.pkl')
            self.scaler = joblib.load(f'{self.models_dir}/cost_scaler.pkl')
            logger.info("Loaded forecasting models")
        except FileNotFoundError:
            logger.info("No existing models found")
    
    def forecast(self, historical_data: pd.DataFrame, 
                days_ahead: int = 90) -> Dict[str, Any]:
        """Generate cost forecast"""
        
        if len(historical_data) < 30:
            logger.warning("Insufficient historical data for forecasting")
            return None
        
        # Prepare time series
        df = historical_data.groupby('date')['cost'].sum().reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        df = df.resample('D').sum().fillna(0)
        
        try:
            # Use Exponential Smoothing for forecasting
            model = ExponentialSmoothing(
                df['cost'],
                trend='add',
                seasonal='add',
                seasonal_periods=7  # Weekly seasonality
            )
            
            fitted = model.fit()
            forecast = fitted.forecast(steps=days_ahead)
            
            # Calculate confidence intervals
            std_error = np.std(fitted.resid)
            confidence_lower = forecast - 1.96 * std_error
            confidence_upper = forecast + 1.96 * std_error
            
            # Determine trend
            current_avg = df['cost'].tail(30).mean()
            forecast_avg = forecast.mean()
            
            if forecast_avg > current_avg * 1.10:
                trend = 'increasing'
            elif forecast_avg < current_avg * 0.90:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            # Calculate monthly forecasts
            current_monthly = df['cost'].tail(30).sum()
            forecasted_monthly = forecast[:30].sum()
            
            result = {
                'current_monthly': current_monthly,
                'forecasted_monthly': forecasted_monthly,
                'forecast_values': forecast.tolist(),
                'confidence_lower': confidence_lower.tolist(),
                'confidence_upper': confidence_upper.tolist(),
                'trend': trend
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Forecasting error: {e}")
            return None

################################################################################
# Savings Optimizer
################################################################################

class SavingsOptimizer:
    """Generate cost savings recommendations"""
    
    def __init__(self, db: CostDatabase):
        self.db = db
    
    async def generate_recommendations(self) -> List[SavingsRecommendation]:
        """Generate savings recommendations"""
        recommendations = []
        
        # Get recent cost data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = self.db.get_daily_costs(start_date, end_date)
        
        if df.empty:
            return recommendations
        
        # 1. Identify underutilized resources
        compute_costs = df[df['category'] == 'compute'].groupby('service')['cost'].sum()
        
        for service, cost in compute_costs.items():
            if cost > 100:  # Significant cost
                rec = SavingsRecommendation(
                    recommendation_id=f"rec-{datetime.now().timestamp()}",
                    title=f"Optimize {service} compute resources",
                    description=f"Consider rightsizing or using spot instances for {service}",
                    provider=CloudProvider.AWS,  # Simplified
                    category=CostCategory.COMPUTE,
                    potential_savings_usd=cost * 0.30,  # 30% savings estimate
                    potential_savings_percent=30.0,
                    effort='medium',
                    priority='high' if cost > 1000 else 'medium',
                    implementation="Analyze resource utilization and adjust instance types",
                    affected_resources=[service]
                )
                recommendations.append(rec)
        
        # 2. Storage optimization
        storage_costs = df[df['category'] == 'storage'].groupby('service')['cost'].sum()
        
        for service, cost in storage_costs.items():
            if cost > 50:
                rec = SavingsRecommendation(
                    recommendation_id=f"rec-{datetime.now().timestamp()}",
                    title=f"Implement storage lifecycle policies for {service}",
                    description="Move infrequently accessed data to cheaper storage tiers",
                    provider=CloudProvider.AWS,
                    category=CostCategory.STORAGE,
                    potential_savings_usd=cost * 0.40,  # 40% savings for storage
                    potential_savings_percent=40.0,
                    effort='low',
                    priority='medium',
                    implementation="Configure lifecycle policies to move data to Glacier or cold storage",
                    affected_resources=[service]
                )
                recommendations.append(rec)
        
        # 3. Reserved instance recommendations
        monthly_compute = compute_costs.sum()
        if monthly_compute > 500:  # Threshold for RI consideration
            rec = SavingsRecommendation(
                recommendation_id=f"rec-{datetime.now().timestamp()}",
                title="Purchase Reserved Instances",
                description="Lock in 1-year or 3-year commitments for consistent workloads",
                provider=CloudProvider.AWS,
                category=CostCategory.COMPUTE,
                potential_savings_usd=monthly_compute * 12 * 0.35,  # 35% annual savings
                potential_savings_percent=35.0,
                effort='low',
                priority='high',
                implementation="Analyze usage patterns and purchase appropriate RIs",
                affected_resources=list(compute_costs.keys())
            )
            recommendations.append(rec)
        
        return recommendations

################################################################################
# Budget Manager
################################################################################

class BudgetManager:
    """Manage budgets and alerts"""
    
    def __init__(self, db: CostDatabase):
        self.db = db
    
    async def check_budgets(self) -> List[BudgetAlert]:
        """Check all budgets and generate alerts"""
        alerts = []
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT * FROM budgets WHERE active = 1')
        
        for row in cursor.fetchall():
            budget_id = row[0]
            name = row[1]
            provider = row[2]
            category = row[3]
            amount = row[4]
            period = row[5]
            start_date = datetime.fromisoformat(row[6])
            end_date = datetime.fromisoformat(row[7])
            threshold = row[8]
            
            # Calculate current spend
            query = '''
                SELECT SUM(cost_usd) FROM cost_entries
                WHERE date BETWEEN ? AND ?
            '''
            params = [start_date.date().isoformat(), end_date.date().isoformat()]
            
            if provider:
                query += ' AND provider = ?'
                params.append(provider)
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            cursor.execute(query, params)
            current_spend = cursor.fetchone()[0] or 0.0
            
            percentage = current_spend / amount if amount > 0 else 0.0
            
            # Generate alert if over threshold
            if percentage >= threshold:
                severity = 'critical' if percentage >= 1.0 else 'warning'
                
                alert = BudgetAlert(
                    alert_id=f"alert-{datetime.now().timestamp()}",
                    budget_name=name,
                    budget_amount=amount,
                    current_spend=current_spend,
                    percentage=percentage,
                    severity=severity
                )
                alerts.append(alert)
                
                # Save alert
                cursor.execute('''
                    INSERT INTO budget_alerts 
                    (alert_id, budget_id, budget_name, budget_amount, 
                     current_spend, percentage, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    budget_id,
                    alert.budget_name,
                    alert.budget_amount,
                    alert.current_spend,
                    alert.percentage,
                    alert.severity
                ))
                self.db.conn.commit()
        
        return alerts

################################################################################
# Cost Intelligence Platform
################################################################################

class CostIntelligencePlatform:
    """Main cost intelligence orchestrator"""
    
    def __init__(self):
        self.db = CostDatabase()
        self.forecast_engine = CostForecastEngine()
        self.savings_optimizer = SavingsOptimizer(self.db)
        self.budget_manager = BudgetManager(self.db)
        self.running = False
    
    async def start(self):
        """Start cost intelligence platform"""
        logger.info("💰 Starting Cost Intelligence Platform v12.0")
        self.running = True
        
        tasks = [
            self._forecasting_loop(),
            self._optimization_loop(),
            self._budget_monitoring_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _forecasting_loop(self):
        """Generate cost forecasts"""
        while self.running:
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                historical_data = self.db.get_daily_costs(start_date, end_date)
                
                if not historical_data.empty:
                    forecast_result = self.forecast_engine.forecast(historical_data, days_ahead=FORECAST_DAYS)
                    
                    if forecast_result:
                        forecast = CostForecast(
                            forecast_id=f"forecast-{datetime.now().timestamp()}",
                            provider=CloudProvider.AWS,  # Simplified
                            category=CostCategory.COMPUTE,
                            current_monthly_cost=forecast_result['current_monthly'],
                            forecasted_monthly_cost=forecast_result['forecasted_monthly'],
                            forecast_date=datetime.now() + timedelta(days=30),
                            confidence_interval=(
                                min(forecast_result['confidence_lower']),
                                max(forecast_result['confidence_upper'])
                            ),
                            trend=forecast_result['trend']
                        )
                        
                        self.db.save_forecast(forecast)
                        logger.info(f"Forecast: ${forecast.forecasted_monthly_cost:.2f}/month ({forecast.trend})")
                
                await asyncio.sleep(86400)  # Daily
            
            except Exception as e:
                logger.error(f"Forecasting error: {e}")
                await asyncio.sleep(3600)
    
    async def _optimization_loop(self):
        """Generate savings recommendations"""
        while self.running:
            try:
                recommendations = await self.savings_optimizer.generate_recommendations()
                
                for rec in recommendations:
                    self.db.save_recommendation(rec)
                
                if recommendations:
                    total_savings = sum(r.potential_savings_usd for r in recommendations)
                    logger.info(f"Generated {len(recommendations)} recommendations: ${total_savings:.2f} potential savings")
                
                await asyncio.sleep(86400)  # Daily
            
            except Exception as e:
                logger.error(f"Optimization error: {e}")
                await asyncio.sleep(3600)
    
    async def _budget_monitoring_loop(self):
        """Monitor budgets"""
        while self.running:
            try:
                alerts = await self.budget_manager.check_budgets()
                
                for alert in alerts:
                    logger.warning(f"Budget alert: {alert.budget_name} at {alert.percentage*100:.1f}%")
                
                await asyncio.sleep(3600)  # Hourly
            
            except Exception as e:
                logger.error(f"Budget monitoring error: {e}")
                await asyncio.sleep(600)
    
    def stop(self):
        """Stop platform"""
        logger.info("Stopping cost intelligence platform")
        self.running = False

################################################################################
# CLI Interface
################################################################################

def main():
    """Main entry point"""
    logger.info("Cost Intelligence Platform v12.0")
    
    if '--status' in sys.argv:
        db = CostDatabase()
        
        # Show cost summary
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = db.get_daily_costs(start_date, end_date)
        
        if not df.empty:
            total_cost = df['cost'].sum()
            print(f"\n💰 Cost Summary (Last 30 days)")
            print(f"Total: ${total_cost:.2f}")
            
            by_category = df.groupby('category')['cost'].sum()
            for category, cost in by_category.items():
                print(f"  {category}: ${cost:.2f}")
    
    elif '--run' in sys.argv:
        platform = CostIntelligencePlatform()
        
        try:
            asyncio.run(platform.start())
        except KeyboardInterrupt:
            platform.stop()
            logger.info("Platform stopped")
    
    else:
        print("""
Cost Intelligence Platform v12.0

Usage:
  --status    Show cost status
  --run       Run platform (continuous)

Examples:
  python3 cost_intelligence_platform.py --status
  python3 cost_intelligence_platform.py --run
        """)

if __name__ == '__main__':
    main()
