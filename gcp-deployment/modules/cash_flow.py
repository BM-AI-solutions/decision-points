import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from utils.logger import setup_logger

logger = setup_logger("modules.cash_flow")

class CashFlowManager:
    """Manager for business cash flow analysis and forecasting."""

    def __init__(self):
        """Initialize the Cash Flow Manager."""
        pass

    async def calculate_cash_flow(
        self, 
        business_model_name: str, 
        implemented_features: List[str]
    ) -> Dict[str, Any]:
        """Calculate cash flow for a business with implemented features.

        Args:
            business_model_name: Business model name
            implemented_features: List of implemented features

        Returns:
            Cash flow data
        """
        logger.info(f"Calculating cash flow for: {business_model_name}")

        # Base revenue estimate based on business model type
        base_revenue = 0.0
        if "dropshipping" in business_model_name.lower():
            base_revenue = 1500.0
        elif "print on demand" in business_model_name.lower():
            base_revenue = 1200.0
        elif "knowledge products" in business_model_name.lower():
            base_revenue = 2000.0
        elif "ai-generated" in business_model_name.lower():
            base_revenue = 1800.0
        elif "subscription" in business_model_name.lower():
            base_revenue = 2500.0
        elif "saas" in business_model_name.lower():
            base_revenue = 3500.0
        else:
            base_revenue = 1000.0

        # Calculate additional revenue from features
        feature_revenue = {
            "automated upsell system": 500.0,
            "abandoned cart recovery": 400.0,
            "tiered access system": 700.0,
            "affiliate program": 600.0,
            "automated marketing funnel": 450.0,
            "dynamic pricing engine": 600.0,
            "one-click upsells": 550.0,
            "feature-based pricing tiers": 800.0,
            "annual subscription discount": 450.0,
            "api access premium": 650.0,
            "referral system": 350.0
        }

        total_feature_revenue = 0.0
        for feature in implemented_features:
            feature_lower = feature.lower()
            for key in feature_revenue:
                if key in feature_lower:
                    total_feature_revenue += feature_revenue[key]
                    break
            else:
                # If no key matches, add default revenue
                total_feature_revenue += 200.0

        total_revenue = base_revenue + total_feature_revenue

        # Define revenue streams based on implemented features
        revenue_streams = ["Base Sales"]
        for feature in implemented_features:
            feature_lower = feature.lower()
            if "upsell" in feature_lower:
                revenue_streams.append("Upsell Revenue")
            elif "cart" in feature_lower and "recovery" in feature_lower:
                revenue_streams.append("Recovered Cart Sales")
            elif "tier" in feature_lower or "pricing" in feature_lower:
                revenue_streams.append("Premium Tier Subscriptions")
            elif "affiliate" in feature_lower:
                revenue_streams.append("Affiliate Commission")
            elif "marketing" in feature_lower or "funnel" in feature_lower:
                revenue_streams.append("Funnel Conversions")
            elif "referral" in feature_lower:
                revenue_streams.append("Referral Revenue")

        # Remove duplicates
        revenue_streams = list(dict.fromkeys(revenue_streams))

        # Calculate automation percentage
        automation_percentage = 80  # Base automation
        automation_percentage += min(20, len(implemented_features) * 4)  # Add for features
        automation_percentage = min(98, automation_percentage)  # Cap at 98%

        return {
            "revenue_streams": revenue_streams,
            "estimated_monthly_revenue": total_revenue,
            "payment_methods": ["Credit Card", "PayPal", "Bank Transfer"],
            "payout_schedule": "Bi-weekly",
            "automated_percentage": automation_percentage,
            "expenses": {
                "fixed": random.uniform(total_revenue * 0.1, total_revenue * 0.3),
                "variable": random.uniform(total_revenue * 0.05, total_revenue * 0.2)
            },
            "profit_margin": random.uniform(0.5, 0.8),
            "break_even_point": random.uniform(total_revenue * 0.2, total_revenue * 0.4)
        }

    async def generate_cash_flow_forecast(
        self, 
        current_revenue: float, 
        months: int = 12,
        growth_rate: float = 0.1
    ) -> Dict[str, Any]:
        """Generate a cash flow forecast for future months.

        Args:
            current_revenue: Current monthly revenue
            months: Number of months to forecast
            growth_rate: Monthly growth rate

        Returns:
            Cash flow forecast
        """
        logger.info(f"Generating cash flow forecast for {months} months")

        # Generate forecast data
        monthly_forecast = []
        current_date = datetime.now()

        for i in range(months):
            # Calculate month date
            month_date = current_date + timedelta(days=30*i)
            month_str = month_date.strftime("%Y-%m")

            # Calculate revenue with growth
            revenue = current_revenue * (1 + growth_rate) ** i

            # Calculate expenses (fixed + variable)
            fixed_expenses = current_revenue * 0.2  # 20% of initial revenue
            variable_expenses = revenue * 0.3  # 30% of current revenue

            # Calculate profit
            profit = revenue - fixed_expenses - variable_expenses

            monthly_forecast.append({
                "month": month_str,
                "revenue": revenue,
                "expenses": fixed_expenses + variable_expenses,
                "profit": profit,
                "growth": i > 0 and (revenue / monthly_forecast[i-1]["revenue"] - 1) * 100 or 0
            })

        # Calculate quarterly and annual aggregates
        quarterly_forecast = []
        for q in range(months // 3):
            start_idx = q * 3
            end_idx = min(start_idx + 3, months)
            quarter_months = monthly_forecast[start_idx:end_idx]

            quarterly_forecast.append({
                "quarter": f"Q{q+1}",
                "revenue": sum(m["revenue"] for m in quarter_months),
                "expenses": sum(m["expenses"] for m in quarter_months),
                "profit": sum(m["profit"] for m in quarter_months)
            })

        return {
            "monthly_forecast": monthly_forecast,
            "quarterly_forecast": quarterly_forecast,
            "total_revenue": sum(m["revenue"] for m in monthly_forecast),
            "total_profit": sum(m["profit"] for m in monthly_forecast),
            "average_monthly_growth": growth_rate * 100,
            "projected_annual_revenue": sum(m["revenue"] for m in monthly_forecast),
            "roi": (sum(m["profit"] for m in monthly_forecast) / (current_revenue * 0.2 * months)) if months > 0 else 0
        }

    async def generate_cash_flow_report(
        self,
        business_model_name: str,
        implemented_features: List[str],
        months: int = 12
    ) -> Dict[str, Any]:
        """Generate a comprehensive cash flow report.

        Args:
            business_model_name: Business model name
            implemented_features: List of implemented features
            months: Number of months to forecast

        Returns:
            Comprehensive cash flow report
        """
        logger.info(f"Generating cash flow report for: {business_model_name}")

        # Calculate current cash flow
        cash_flow = await self.calculate_cash_flow(business_model_name, implemented_features)

        # Generate forecast
        forecast = await self.generate_cash_flow_forecast(
            cash_flow["estimated_monthly_revenue"],
            months=months
        )

        # Generate revenue breakdown by stream
        revenue_breakdown = []
        total_revenue = cash_flow["estimated_monthly_revenue"]
        remaining_revenue = total_revenue

        for i, stream in enumerate(cash_flow["revenue_streams"]):
            # Last stream gets the remainder to ensure total adds up exactly
            if i == len(cash_flow["revenue_streams"]) - 1:
                stream_revenue = remaining_revenue
            else:
                # Distribute revenue with some randomness
                portion = random.uniform(0.1, 0.5)
                stream_revenue = total_revenue * portion
                remaining_revenue -= stream_revenue

            revenue_breakdown.append({
                "stream": stream,
                "amount": stream_revenue,
                "percentage": (stream_revenue / total_revenue) * 100
            })

        return {
            "business_model": business_model_name,
            "implemented_features": implemented_features,
            "current_cash_flow": cash_flow,
            "forecast": forecast,
            "revenue_breakdown": revenue_breakdown,
            "kpis": {
                "monthly_recurring_revenue": cash_flow["estimated_monthly_revenue"],
                "annual_recurring_revenue": cash_flow["estimated_monthly_revenue"] * 12,
                "customer_lifetime_value": cash_flow["estimated_monthly_revenue"] * random.uniform(6, 24),
                "customer_acquisition_cost": cash_flow["estimated_monthly_revenue"] * random.uniform(0.1, 0.3),
                "roi": random.uniform(2.0, 8.0),
                "break_even_timeline": f"{random.randint(1, 6)} months"
            }
        }