"""
Data analyzer for Claude usage analytics
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

from ..providers.claude_code_reader import ClaudeCodeReader
from .config_loader import get_config

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes Claude usage data for insights and recommendations"""
    
    def __init__(self, reader: Optional[ClaudeCodeReader] = None):
        """Initialize analyzer with a reader instance"""
        self.reader = reader or ClaudeCodeReader()
        self.config = get_config()
        
    def get_claude_usage(self) -> Dict[str, Any]:
        """Get basic Claude usage data"""
        return self.reader.get_usage_data()
        
    def get_current_month_analysis(self) -> Dict[str, Any]:
        """Get analysis for the current month"""
        # Get start of current month
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        
        # Get usage data for current month
        usage = self.reader.get_usage_data(since_date=month_start)
        
        # Get session blocks for overflow analysis
        self.reader._update_session_blocks()
        month_blocks = [b for b in self.reader._session_blocks 
                       if b.end_time >= month_start or b.is_active]
        
        # Analyze overflow sessions
        plan = self.config.get_subscription_plan()
        plan_info = self.config.get_plan_info(plan)
        session_limit = plan_info.get('session_token_limit', 220000)
        
        overflow_sessions = []
        total_overflow_tokens = 0
        
        for block in month_blocks:
            if block.total_tokens > session_limit:
                overflow_tokens = block.total_tokens - session_limit
                overflow_sessions.append({
                    'start_time': block.start_time,
                    'tokens': block.total_tokens,
                    'overflow': overflow_tokens
                })
                total_overflow_tokens += overflow_tokens
        
        return {
            'total_tokens': usage['total_tokens'],
            'total_input_tokens': usage['total_input_tokens'],
            'total_output_tokens': usage['total_output_tokens'],
            'total_cost': usage['total_cost'],
            'session_count': usage['session_count'],
            'overflow_sessions': overflow_sessions,
            'total_overflow_tokens': total_overflow_tokens,
            'since_date': month_start
        }
        
    def get_value_analysis_data(self, period: str = 'month') -> Dict[str, Any]:
        """Get value analysis data for the specified period"""
        # Determine date range
        now = datetime.now()
        
        if period == 'month':
            # Current month to date
            start_date = datetime(now.year, now.month, 1)
            days_in_month = 31 if now.month in [1, 3, 5, 7, 8, 10, 12] else 30
            if now.month == 2:
                days_in_month = 29 if now.year % 4 == 0 else 28
            days_passed = now.day
        elif period == '30days':
            # Last 30 days
            start_date = now - timedelta(days=30)
            days_in_month = 30
            days_passed = 30
        else:
            # Default to month
            start_date = datetime(now.year, now.month, 1)
            days_in_month = 31
            days_passed = now.day
            
        # Get usage data
        usage = self.reader.get_usage_data(since_date=start_date)
        
        # Get subscription info
        plan = self.config.get_subscription_plan()
        plan_info = self.config.get_plan_info(plan)
        subscription_cost = plan_info.get('monthly_cost', 200)
        monthly_tokens = plan_info.get('session_token_limit', 220000) * plan_info.get('sessions_per_month', 120)
        
        # Calculate prorated tokens available
        tokens_available = int(monthly_tokens * days_passed / days_in_month)
        tokens_used = usage['total_tokens']
        
        # Calculate API cost
        api_cost = usage['total_cost']
        
        # Project to full month if needed
        if period == 'month' and days_passed < days_in_month:
            projected_multiplier = days_in_month / days_passed
            api_cost_projected = api_cost * projected_multiplier
        else:
            api_cost_projected = api_cost
            
        # Calculate efficiency
        efficiency = (tokens_used / tokens_available * 100) if tokens_available > 0 else 0
        
        # Calculate break-even efficiency
        # API cost if we used all available tokens
        cost_per_token = api_cost / tokens_used if tokens_used > 0 else 0.00007128
        api_cost_for_all_tokens = tokens_available * cost_per_token
        breakeven_efficiency = (subscription_cost / api_cost_for_all_tokens * 100) if api_cost_for_all_tokens > 0 else 100
        
        # Calculate burn rate
        burn_rate = self.reader.calculate_hourly_burn_rate()
        burn_rate_per_min = burn_rate / 60 if burn_rate > 0 else 0
        cost_per_min = burn_rate_per_min * cost_per_token
        
        # Get overflow sessions
        month_analysis = self.get_current_month_analysis()
        
        # Get session blocks for detailed analysis
        self.reader._update_session_blocks()
        period_blocks = [b for b in self.reader._session_blocks 
                        if b.end_time >= start_date or b.is_active]
        
        return {
            'api_cost': api_cost_projected,
            'subscription_cost': subscription_cost,
            'tokens_used': tokens_used,
            'tokens_available': tokens_available,
            'efficiency': efficiency,
            'breakeven_efficiency': breakeven_efficiency,
            'burn_rate_per_min': cost_per_min,
            'overflow_sessions': month_analysis['overflow_sessions'],
            'total_overflow_tokens': month_analysis['total_overflow_tokens'],
            'session_blocks': period_blocks
        }