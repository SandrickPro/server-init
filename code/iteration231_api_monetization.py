#!/usr/bin/env python3
"""
Server Init - Iteration 231: API Monetization Platform
Платформа монетизации API

Функционал:
- Pricing Plans - тарифные планы
- Usage Metering - учёт использования
- Billing Integration - интеграция биллинга
- Quota Management - управление квотами
- Revenue Analytics - аналитика доходов
- Subscription Management - управление подписками
- Invoice Generation - генерация счетов
- Payment Processing - обработка платежей
"""

import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid


class PlanType(Enum):
    """Тип плана"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(Enum):
    """Цикл биллинга"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    PAY_AS_YOU_GO = "pay_as_you_go"


class SubscriptionStatus(Enum):
    """Статус подписки"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class InvoiceStatus(Enum):
    """Статус счёта"""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


class MetricType(Enum):
    """Тип метрики"""
    API_CALLS = "api_calls"
    DATA_TRANSFER = "data_transfer"
    STORAGE = "storage"
    COMPUTE = "compute"
    USERS = "users"


@dataclass
class PricingTier:
    """Тарифный уровень"""
    tier_id: str
    from_units: int = 0
    to_units: int = 0  # 0 = unlimited
    price_per_unit: float = 0


@dataclass
class PricingPlan:
    """Тарифный план"""
    plan_id: str
    name: str = ""
    plan_type: PlanType = PlanType.FREE
    
    # Pricing
    base_price: float = 0
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    
    # Limits
    rate_limit_per_second: int = 10
    monthly_quota: int = 1000
    
    # Features
    features: List[str] = field(default_factory=list)
    
    # Tiers for usage-based pricing
    tiers: List[PricingTier] = field(default_factory=list)
    
    # Active
    is_active: bool = True


@dataclass
class Customer:
    """Клиент"""
    customer_id: str
    name: str = ""
    email: str = ""
    company: str = ""
    
    # Billing
    billing_email: str = ""
    billing_address: str = ""
    payment_method: str = ""  # card_xxxx
    
    # Status
    is_active: bool = True
    
    # Created
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    """Подписка"""
    subscription_id: str
    customer_id: str = ""
    plan_id: str = ""
    
    # Status
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Period
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Usage
    current_period_usage: int = 0
    
    # Billing
    next_billing_date: datetime = field(default_factory=datetime.now)


@dataclass
class UsageRecord:
    """Запись использования"""
    record_id: str
    subscription_id: str = ""
    
    # Metric
    metric_type: MetricType = MetricType.API_CALLS
    quantity: int = 0
    
    # Endpoint
    endpoint: str = ""
    
    # Time
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Invoice:
    """Счёт"""
    invoice_id: str
    customer_id: str = ""
    subscription_id: str = ""
    
    # Period
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    
    # Line items
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    
    # Amounts
    subtotal: float = 0
    tax: float = 0
    total: float = 0
    
    # Status
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    # Due date
    due_date: datetime = field(default_factory=datetime.now)
    
    # Paid
    paid_at: Optional[datetime] = None


@dataclass
class RevenueMetrics:
    """Метрики доходов"""
    period: str = ""
    mrr: float = 0  # Monthly Recurring Revenue
    arr: float = 0  # Annual Recurring Revenue
    total_customers: int = 0
    active_subscriptions: int = 0
    churn_rate: float = 0
    arpu: float = 0  # Average Revenue Per User


class PlanManager:
    """Менеджер планов"""
    
    def __init__(self):
        self.plans: Dict[str, PricingPlan] = {}
        
    def create_plan(self, name: str, plan_type: PlanType,
                   base_price: float, billing_cycle: BillingCycle,
                   rate_limit: int, monthly_quota: int,
                   features: List[str] = None) -> PricingPlan:
        """Создание плана"""
        plan = PricingPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            name=name,
            plan_type=plan_type,
            base_price=base_price,
            billing_cycle=billing_cycle,
            rate_limit_per_second=rate_limit,
            monthly_quota=monthly_quota,
            features=features or []
        )
        self.plans[plan.plan_id] = plan
        return plan
        
    def add_tier(self, plan_id: str, from_units: int,
                to_units: int, price_per_unit: float) -> Optional[PricingTier]:
        """Добавление тарифного уровня"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None
            
        tier = PricingTier(
            tier_id=f"tier_{uuid.uuid4().hex[:8]}",
            from_units=from_units,
            to_units=to_units,
            price_per_unit=price_per_unit
        )
        plan.tiers.append(tier)
        return tier


class UsageMetering:
    """Учёт использования"""
    
    def __init__(self):
        self.records: List[UsageRecord] = []
        
    def record(self, subscription_id: str, metric_type: MetricType,
              quantity: int, endpoint: str = "") -> UsageRecord:
        """Запись использования"""
        record = UsageRecord(
            record_id=f"usage_{uuid.uuid4().hex[:8]}",
            subscription_id=subscription_id,
            metric_type=metric_type,
            quantity=quantity,
            endpoint=endpoint
        )
        self.records.append(record)
        return record
        
    def get_usage(self, subscription_id: str, 
                 start_date: datetime = None) -> Dict[MetricType, int]:
        """Получение использования"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
            
        usage = {}
        for record in self.records:
            if record.subscription_id == subscription_id and \
               record.timestamp >= start_date:
                if record.metric_type not in usage:
                    usage[record.metric_type] = 0
                usage[record.metric_type] += record.quantity
                
        return usage


class BillingEngine:
    """Биллинговый движок"""
    
    def __init__(self, plan_manager: PlanManager, metering: UsageMetering):
        self.plan_manager = plan_manager
        self.metering = metering
        
    def calculate_usage_cost(self, plan_id: str, usage: int) -> float:
        """Расчёт стоимости использования"""
        plan = self.plan_manager.plans.get(plan_id)
        if not plan or not plan.tiers:
            return 0
            
        cost = 0
        remaining = usage
        
        for tier in sorted(plan.tiers, key=lambda t: t.from_units):
            if remaining <= 0:
                break
                
            tier_units = tier.to_units - tier.from_units if tier.to_units > 0 else remaining
            units_in_tier = min(remaining, tier_units)
            
            cost += units_in_tier * tier.price_per_unit
            remaining -= units_in_tier
            
        return cost
        
    def generate_invoice(self, subscription: Subscription, plan: PricingPlan,
                        customer_id: str) -> Invoice:
        """Генерация счёта"""
        usage = self.metering.get_usage(subscription.subscription_id)
        api_calls = usage.get(MetricType.API_CALLS, 0)
        
        # Base price
        subtotal = plan.base_price
        
        # Usage overage
        if api_calls > plan.monthly_quota:
            overage = api_calls - plan.monthly_quota
            overage_cost = self.calculate_usage_cost(plan.plan_id, overage)
            subtotal += overage_cost
            
        tax = subtotal * 0.1  # 10% tax
        total = subtotal + tax
        
        invoice = Invoice(
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}",
            customer_id=customer_id,
            subscription_id=subscription.subscription_id,
            period_end=datetime.now(),
            period_start=datetime.now() - timedelta(days=30),
            line_items=[
                {"description": f"{plan.name} Plan", "amount": plan.base_price},
                {"description": f"API Calls: {api_calls:,}", "amount": 0}
            ],
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=InvoiceStatus.PENDING,
            due_date=datetime.now() + timedelta(days=30)
        )
        
        return invoice


class APIMonetizationPlatform:
    """Платформа монетизации API"""
    
    def __init__(self):
        self.plan_manager = PlanManager()
        self.metering = UsageMetering()
        self.billing = BillingEngine(self.plan_manager, self.metering)
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        
    def create_plan(self, name: str, plan_type: PlanType,
                   base_price: float, features: List[str]) -> PricingPlan:
        """Создание плана"""
        rate_limits = {
            PlanType.FREE: 10,
            PlanType.STARTER: 50,
            PlanType.PROFESSIONAL: 200,
            PlanType.ENTERPRISE: 1000
        }
        
        quotas = {
            PlanType.FREE: 1000,
            PlanType.STARTER: 10000,
            PlanType.PROFESSIONAL: 100000,
            PlanType.ENTERPRISE: 1000000
        }
        
        return self.plan_manager.create_plan(
            name, plan_type, base_price, BillingCycle.MONTHLY,
            rate_limits.get(plan_type, 10),
            quotas.get(plan_type, 1000),
            features
        )
        
    def register_customer(self, name: str, email: str,
                         company: str = "") -> Customer:
        """Регистрация клиента"""
        customer = Customer(
            customer_id=f"cust_{uuid.uuid4().hex[:8]}",
            name=name,
            email=email,
            company=company,
            billing_email=email
        )
        self.customers[customer.customer_id] = customer
        return customer
        
    def create_subscription(self, customer_id: str,
                           plan_id: str, trial_days: int = 0) -> Optional[Subscription]:
        """Создание подписки"""
        if customer_id not in self.customers:
            return None
        if plan_id not in self.plan_manager.plans:
            return None
            
        subscription = Subscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.TRIAL if trial_days > 0 else SubscriptionStatus.ACTIVE,
            trial_end=datetime.now() + timedelta(days=trial_days) if trial_days > 0 else None,
            next_billing_date=datetime.now() + timedelta(days=30)
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        return subscription
        
    def record_usage(self, subscription_id: str, api_calls: int,
                    endpoint: str = "/api/v1") -> UsageRecord:
        """Запись использования"""
        record = self.metering.record(
            subscription_id, MetricType.API_CALLS, api_calls, endpoint
        )
        
        # Update subscription usage
        sub = self.subscriptions.get(subscription_id)
        if sub:
            sub.current_period_usage += api_calls
            
        return record
        
    def generate_invoice(self, subscription_id: str) -> Optional[Invoice]:
        """Генерация счёта"""
        sub = self.subscriptions.get(subscription_id)
        if not sub:
            return None
            
        plan = self.plan_manager.plans.get(sub.plan_id)
        if not plan:
            return None
            
        invoice = self.billing.generate_invoice(sub, plan, sub.customer_id)
        self.invoices[invoice.invoice_id] = invoice
        return invoice
        
    def pay_invoice(self, invoice_id: str) -> bool:
        """Оплата счёта"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return False
            
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now()
        return True
        
    def get_revenue_metrics(self) -> RevenueMetrics:
        """Метрики доходов"""
        active_subs = [s for s in self.subscriptions.values() 
                      if s.status == SubscriptionStatus.ACTIVE]
        
        mrr = 0
        for sub in active_subs:
            plan = self.plan_manager.plans.get(sub.plan_id)
            if plan:
                mrr += plan.base_price
                
        return RevenueMetrics(
            period=datetime.now().strftime("%Y-%m"),
            mrr=mrr,
            arr=mrr * 12,
            total_customers=len(self.customers),
            active_subscriptions=len(active_subs),
            arpu=mrr / len(active_subs) if active_subs else 0
        )
        
    def get_statistics(self) -> Dict[str, Any]:
        """Статистика"""
        subs = list(self.subscriptions.values())
        active = [s for s in subs if s.status == SubscriptionStatus.ACTIVE]
        
        by_plan = {}
        for s in subs:
            plan = self.plan_manager.plans.get(s.plan_id)
            if plan:
                t = plan.plan_type.value
                if t not in by_plan:
                    by_plan[t] = 0
                by_plan[t] += 1
                
        invoices = list(self.invoices.values())
        paid = [i for i in invoices if i.status == InvoiceStatus.PAID]
        
        return {
            "total_plans": len(self.plan_manager.plans),
            "total_customers": len(self.customers),
            "total_subscriptions": len(subs),
            "active_subscriptions": len(active),
            "subscriptions_by_plan": by_plan,
            "total_invoices": len(invoices),
            "paid_invoices": len(paid),
            "total_revenue": sum(i.total for i in paid)
        }


# Демонстрация
async def main():
    print("=" * 60)
    print("Server Init - Iteration 231: API Monetization Platform")
    print("=" * 60)
    
    platform = APIMonetizationPlatform()
    print("✓ API Monetization Platform created")
    
    # Create plans
    print("\n💰 Creating Pricing Plans...")
    
    plans_config = [
        ("Free", PlanType.FREE, 0, ["1K requests/month", "Basic support"]),
        ("Starter", PlanType.STARTER, 29, ["10K requests/month", "Email support", "API analytics"]),
        ("Professional", PlanType.PROFESSIONAL, 99, ["100K requests/month", "Priority support", "Advanced analytics", "Webhooks"]),
        ("Enterprise", PlanType.ENTERPRISE, 499, ["1M requests/month", "24/7 support", "SLA", "Custom integrations", "Dedicated manager"]),
    ]
    
    plans = []
    for name, ptype, price, features in plans_config:
        plan = platform.create_plan(name, ptype, price, features)
        plans.append(plan)
        
        # Add usage tiers for paid plans
        if price > 0:
            platform.plan_manager.add_tier(plan.plan_id, 0, plan.monthly_quota, 0)
            platform.plan_manager.add_tier(plan.plan_id, plan.monthly_quota, 0, 0.001)
            
        price_str = f"${price}/mo" if price > 0 else "Free"
        print(f"  ✓ {name}: {price_str} ({plan.monthly_quota:,} calls/mo)")
        
    # Register customers
    print("\n👥 Registering Customers...")
    
    customers_config = [
        ("John Doe", "john@startup.com", "Startup Inc"),
        ("Jane Smith", "jane@techco.com", "Tech Company"),
        ("Bob Wilson", "bob@enterprise.com", "Enterprise Corp"),
        ("Alice Brown", "alice@dev.com", "Dev Studio"),
        ("Charlie Davis", "charlie@app.io", "App Makers"),
    ]
    
    customers = []
    for name, email, company in customers_config:
        customer = platform.register_customer(name, email, company)
        customers.append(customer)
        print(f"  ✓ {name} ({company})")
        
    # Create subscriptions
    print("\n📋 Creating Subscriptions...")
    
    subscriptions = []
    for i, customer in enumerate(customers):
        plan = plans[i % len(plans)]
        trial = 14 if plan.plan_type == PlanType.FREE else 0
        
        sub = platform.create_subscription(customer.customer_id, plan.plan_id, trial)
        if sub:
            subscriptions.append(sub)
            status = "trial" if trial > 0 else "active"
            print(f"  ✓ {customer.name} -> {plan.name} ({status})")
            
    # Record usage
    print("\n📊 Recording API Usage...")
    
    endpoints = ["/api/v1/users", "/api/v1/orders", "/api/v1/products", "/api/v1/analytics"]
    
    for sub in subscriptions:
        for _ in range(random.randint(5, 20)):
            calls = random.randint(100, 5000)
            endpoint = random.choice(endpoints)
            platform.record_usage(sub.subscription_id, calls, endpoint)
            
    total_usage = sum(s.current_period_usage for s in subscriptions)
    print(f"  ✓ Recorded {total_usage:,} total API calls")
    
    # Generate invoices
    print("\n📄 Generating Invoices...")
    
    invoices = []
    for sub in subscriptions:
        plan = platform.plan_manager.plans.get(sub.plan_id)
        if plan and plan.base_price > 0:
            invoice = platform.generate_invoice(sub.subscription_id)
            if invoice:
                invoices.append(invoice)
                customer = platform.customers.get(sub.customer_id)
                name = customer.name if customer else "unknown"
                print(f"  ✓ {name}: ${invoice.total:.2f}")
                
    # Pay some invoices
    print("\n💳 Processing Payments...")
    
    for invoice in invoices[:3]:
        platform.pay_invoice(invoice.invoice_id)
        customer = platform.customers.get(invoice.customer_id)
        name = customer.name if customer else "unknown"
        print(f"  ✓ {name}: ${invoice.total:.2f} paid")
        
    # Display plans
    print("\n💰 Pricing Plans:")
    
    print("\n  ┌────────────────────┬──────────┬────────────┬─────────────┐")
    print("  │ Plan               │ Price    │ Rate Limit │ Quota       │")
    print("  ├────────────────────┼──────────┼────────────┼─────────────┤")
    
    for plan in platform.plan_manager.plans.values():
        name = plan.name[:18].ljust(18)
        price = f"${plan.base_price:.0f}/mo" if plan.base_price > 0 else "Free"
        price = price[:8].ljust(8)
        rate = f"{plan.rate_limit_per_second}/sec"[:10].ljust(10)
        quota = f"{plan.monthly_quota:,}"[:11].ljust(11)
        
        print(f"  │ {name} │ {price} │ {rate} │ {quota} │")
        
    print("  └────────────────────┴──────────┴────────────┴─────────────┘")
    
    # Subscription breakdown
    print("\n📋 Subscriptions by Plan:")
    
    stats = platform.get_statistics()
    
    plan_icons = {
        "free": "🆓",
        "starter": "🌱",
        "professional": "⭐",
        "enterprise": "🏢",
        "custom": "🔧"
    }
    
    for plan_type, count in stats["subscriptions_by_plan"].items():
        icon = plan_icons.get(plan_type, "📋")
        bar = "█" * count + "░" * (5 - count)
        print(f"  {icon} {plan_type:15s} [{bar}] {count}")
        
    # Usage by customer
    print("\n📊 Customer Usage:")
    
    for sub in subscriptions[:5]:
        customer = platform.customers.get(sub.customer_id)
        plan = platform.plan_manager.plans.get(sub.plan_id)
        
        if customer and plan:
            pct = (sub.current_period_usage / plan.monthly_quota * 100) if plan.monthly_quota > 0 else 0
            bar_len = min(int(pct / 10), 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            
            print(f"  {customer.name:15s}: [{bar}] {sub.current_period_usage:,}/{plan.monthly_quota:,} ({pct:.0f}%)")
            
    # Invoice status
    print("\n📄 Invoice Summary:")
    
    invoice_icons = {
        InvoiceStatus.PAID: "✓",
        InvoiceStatus.PENDING: "○",
        InvoiceStatus.OVERDUE: "⚠",
        InvoiceStatus.VOID: "✗"
    }
    
    for invoice in invoices:
        customer = platform.customers.get(invoice.customer_id)
        name = customer.name if customer else "unknown"
        icon = invoice_icons.get(invoice.status, "?")
        print(f"  {icon} {name}: ${invoice.total:.2f} ({invoice.status.value})")
        
    # Revenue metrics
    print("\n💵 Revenue Metrics:")
    
    metrics = platform.get_revenue_metrics()
    
    print(f"  MRR: ${metrics.mrr:.2f}")
    print(f"  ARR: ${metrics.arr:.2f}")
    print(f"  ARPU: ${metrics.arpu:.2f}")
    print(f"  Active Subscriptions: {metrics.active_subscriptions}")
    
    # Statistics
    print("\n📈 Platform Statistics:")
    
    print(f"\n  Plans: {stats['total_plans']}")
    print(f"  Customers: {stats['total_customers']}")
    print(f"  Active Subscriptions: {stats['active_subscriptions']}")
    print(f"  Invoices: {stats['total_invoices']} ({stats['paid_invoices']} paid)")
    print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
    
    # Dashboard
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│                    API Monetization Dashboard                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Customers:               {stats['total_customers']:>12}                        │")
    print(f"│ Active Subscriptions:          {stats['active_subscriptions']:>12}                        │")
    print(f"│ Monthly Recurring Revenue:     ${metrics.mrr:>11.2f}                       │")
    print("├────────────────────────────────────────────────────────────────────┤")
    print(f"│ Total Invoices:                {stats['total_invoices']:>12}                        │")
    print(f"│ Total Revenue:                 ${stats['total_revenue']:>11.2f}                       │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "=" * 60)
    print("API Monetization Platform initialized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
